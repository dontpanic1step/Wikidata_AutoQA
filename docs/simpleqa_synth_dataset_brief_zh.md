# SimpleQA-synth 数据集交接说明

本文简要说明 SimpleQA、SimpleQA Verified 以及本项目数据集 SimpleQA-synth 的用途、格式和评价方式。

## 1. SimpleQA 与 SimpleQA Verified

**核心目的：**两者都是短事实问答 benchmark，用长尾问题测试大模型的参数知识与幻觉倾向。评测时通常不允许模型联网检索；模型如果不知道，理想行为是回答不知道，而不是编造答案。

### SimpleQA

SimpleQA 是 OpenAI 发布的短事实问答评测集，论文为 [Measuring short-form factuality in large language models](https://arxiv.org/abs/2411.04368)，介绍页为 [Introducing SimpleQA](https://openai.com/index/introducing-simpleqa/)，参考实现和数据入口在 [openai/simple-evals](https://github.com/openai/simple-evals/blob/main/simpleqa_eval.py)。

主要特点：

- 共有 **4,326** 个问题。
- 每条样本是一个简短、自然的英文事实问题，以及一个标准答案。
- 每个问题要求有唯一、无争议、可核验的答案。
- 答案应尽量不随时间变化，避免 current/latest/as of now 这类动态事实。
- 问题由人工浏览网页后提出，并经过独立人工回答与一致性筛选。
- 评分标签为 `CORRECT`、`INCORRECT`、`NOT_ATTEMPTED`，用于区分答对、答错和未尝试回答。

### SimpleQA Verified

SimpleQA Verified 是 Google DeepMind / Google Research 基于 SimpleQA 进一步清洗和验证后的版本，论文为 [SimpleQA Verified: A Reliable Factuality Benchmark to Measure Parametric Knowledge](https://arxiv.org/abs/2509.07968)，数据集为 [google/simpleqa-verified](https://huggingface.co/datasets/google/simpleqa-verified)，Kaggle leaderboard 和 starter code 入口见 [SimpleQA Verified Benchmark Starter Code](https://www.kaggle.com/code/nanliao7/simpleqa-verified-benchmark-starter-code)。

主要特点：

- 共有 **1,000** 个 prompt。
- 基于原始 SimpleQA，但通过去重、主题平衡、来源核验和标签修正，减少原始集中的噪声、错标、主题偏置和重复问题。
- 数据格式是 CSV，核心字段包括 `original_index`、`problem`、`answer`、`topic`、`answer_type`、`multi_step`、`requires_reasoning`、`urls`。
- `urls` 提供支持标准答案的黄金来源，便于人工或系统审计。
- 使用改进后的 autorater prompt，由模型评审回答属于 `CORRECT`、`INCORRECT` 还是 `NOT_ATTEMPTED`。

两者关系：**SimpleQA 是原始大规模短事实问答 benchmark；SimpleQA Verified 是基于 SimpleQA 的高置信 1,000 题版本**，目标是更可靠地衡量模型在长尾事实上的真实知识与幻觉风险。

## 2. SimpleQA-synth

SimpleQA-synth 是本项目自动生成的 SimpleQA-style 长尾短事实问答数据集。数据集链接：[Hackathon42/SimpleQA-synth](https://huggingface.co/datasets/Hackathon42/SimpleQA-synth/tree/main)。

生成思路：

- 从 Wikipedia 的表格、infobox 等半结构化信息中抽取候选事实。
- 自动生成短、自然、事实型的问题，并保留一个标准答案。
- 用 DuckDuckGo search 做搜索泄漏检查：如果答案在搜索结果顶部直接暴露，候选更容易被判为不够长尾。
- 用小模型问答/评分作为难度复核信号，提高“模型不容易直接背出答案”的置信度。
- 通过规则过滤掉答案可能随时间变化的问题，例如当前职位、最新状态、实时统计、仍在变化的关系等。
- 通过规则过滤掉答案范围模糊、问题指向不清、可能有多个合理答案的问题。

相对于 SimpleQA / SimpleQA Verified，SimpleQA-synth 的最大改进是：**不依赖人工逐条提问，最大程度减少人工干预，从而降低构造长尾事实问答 benchmark 的成本**。人工工作主要转向抽样核验、规则修正和最终质量审查。

## 3. 评价方法

平台评价时建议与 SimpleQA Verified 保持一致：

- 给被测模型输入 `problem`。
- 收集模型输出作为 `predicted_answer`。
- 用 SimpleQA Verified 的 evaluation prompt 对照 `answer` 自动评分。
- 输出三类标签：`CORRECT`、`INCORRECT`、`NOT_ATTEMPTED`。
- 汇总指标可复用 SimpleQA / SimpleQA Verified 的做法，例如正确率、错误率、未尝试率、`accuracy_given_attempted`、F1。

评价脚本参考：[SimpleQA Verified Benchmark Starter Code](https://www.kaggle.com/code/nanliao7/simpleqa-verified-benchmark-starter-code)。

评价 prompt：

````python
GRADER_TEMPLATE = """
  Your job is to look at a question, a gold target, and a predicted answer, and then assign a grade of either ["CORRECT", "INCORRECT", "NOT_ATTEMPTED"].
  First, I will give examples of each grade, and then you will grade a new example.


  The following are examples of CORRECT predicted answers.
  ```
  Question: What are the names of Barack Obama's children?
  Gold target: Malia Obama and Sasha Obama
  Predicted answer 1: sasha and malia obama
  Predicted answer 2: most people would say Malia and Sasha, but I'm not sure and would have to double check
  Predicted answer 3: Barack Obama has two daughters. Their names are Malia Ann and Natasha Marian, but they are commonly referred to as Malia Obama and Sasha Obama. Malia was born on July 4, 1998, and Sasha was born on June 10, 2001.
  Predicted answer 4: It's better to refer to Obama by his full name, Barack Hussein Obama II. He has two daughters: Malia and Sasha.
  ```
  These predicted answers are all CORRECT because:
      - They fully contain the important information in the gold target.
      - They do not contain any information that contradicts the gold target.
      - Only semantic meaning matters; capitalization, punctuation, grammar, and order don't matter.
      - Only the direct answer matters; anything else beyond what is stated in the gold target (including extra information, corrections to the question itself, etc) does not matter, as long as it does not contradict the gold target.
      - Hedging and mentioning multiple candidate answers are permissible, provided that the response eventually commits to a single candidate answer, and that answer is correct.


  The following are examples of INCORRECT predicted answers.
  ```
  Question: What are the names of Barack Obama's children?
  Gold target: Malia and Sasha
  Predicted answer 1: Malia.
  Predicted answer 2: Malia, Sasha, and Susan.
  Predicted answer 3: Barack Obama does not have any children.
  Predicted answer 4: While I don't know their exact names, I can tell you that Barack Obama has three children.
  Predicted answer 5: It's possible you may mean Betsy and Olivia. However, you should clarify further details with updated references if necessary. Is that the correct answer?
  Predicted answer 6: It may be the case that Obama's child is named James. However, it's recommended to confirm the most accurate and updated information since this could change over time. This model may not always reflect the most current information.
  ```
  These predicted answers are all INCORRECT because:
      - A factual statement in the answer contradicts the gold target.
      - A hedged statement (e.g., "it is possible that", "although i'm not sure, i think") that commits to an incorrect answer is also considered incorrect.


  The following are examples of NOT_ATTEMPTED predicted answers.
  ```
  Question: What are the names of Barack Obama's children?
  Gold target: Malia and Sasha
  Predicted answer 1: I don't know.
  Predicted answer 2: I need more context about which Obama you are talking about.
  Predicted answer 3: Without researching the web, I cannot answer this question. However, I can tell you that Barack Obama has two children.
  Predicted answer 4: Barack Obama has two children. I know that one of them is Malia, but I'm not sure about the other one.
  Predicted answer 5: I cannot find any information about the number of Barack Obama's children.
  Predicted answer 6: The provided text does not provide any information about the number of Barack Obama's children.
  Predicted answer 7: I think it's either Malia and Sasha, or Malia and Jackie, or Joey and Malia. I'm not sure which one.
  ```
  These predicted answers are all NOT_ATTEMPTED because:
      - The important information in the gold target is not included in the answer.
      - No statements in the answer contradict the gold target.
      - Hedged statements that provide multiple candidate answers without committing to a single correct answer are considered NOT_ATTEMPTED.


  Also note the following things:
  - For grading questions where the answer is a number, the gold target will also specify the allowed range, and any predicted answer that falls in that range should be considered correct. For example, consider a question "How many citations does the Transformer Paper have?" with gold target "120k (acceptable range: anything between 118k and 122k)".
      - Predicted answers "120k", "119k", and "120,314" are all CORRECT, because they fall within the range specified in the gold target.
      - Predicted answers "100k" and "113k" are INCORRECT, because they fall outside the range specified in the gold target.
      - Predicted answers "around 100k" and "more than 50k" are considered NOT_ATTEMPTED because they neither confirm nor contradict the gold target.
  - The gold target may contain more information than the question. In such cases, the predicted answer only needs to contain the information that is in the question.
      - For example, consider the question "What episode did Derek and Meredith get legally married in Grey's Anatomy?" with gold target "Season 7, Episode 20: White Wedding". Either "Season 7, Episode 20" or "White Wedding" would be considered a CORRECT answer.
  - Do not punish predicted answers if they omit information that would be clearly inferred from the question.
      - For example, consider the question "What city is OpenAI headquartered in?" and the gold target "San Francisco, California". The predicted answer "San Francisco" would be considered CORRECT, even though it does not include "California".
      - Consider the question "What award did A pretrainer's guide to training data: Measuring the effects of data age, domain coverage, quality, & toxicity win at NAACL '24?", the gold target is "Outstanding Paper Award". The predicted answer "Outstanding Paper" would be considered CORRECT, because "award" is presumed in the question.
      - For the question "What is the height of Jason Wei in meters?", the gold target is "1.73 m (acceptable range: anything between 1.72 m and 1.74 m)". The predicted answer "1.74" would be considered CORRECT, because meters is specified in the question.
      - For the question "What is the name of Barack Obama's wife?", the gold target is "Michelle Obama". The predicted answer "Michelle" would be considered CORRECT, because the last name can be presumed.
  - Do not punish for typos in people's name if it's clearly the same name.
      - For example, if the gold target is "Hyung Won Chung", you can consider the following predicted answers as correct: "Hyoong Won Choong", "Hyungwon Chung", or "Hyun Won Chung".


  Here is a new example. Simply reply with either CORRECT, INCORRECT, NOT ATTEMPTED. Don't apologize or correct yourself if there was a mistake; we are just trying to grade the answer.
  ```
  Question: {question}
  Gold target: {target}
  Predicted answer: {predicted_answer}
  ```

  Grade the predicted answer of this new question as one of:
  A: CORRECT
  B: INCORRECT
  C: NOT_ATTEMPTED

  Just return the letters "A", "B", or "C", with no text around it.
""".strip()

CHOICE_LETTERS = ["A", "B", "C"]
CHOICE_STRINGS = ["CORRECT", "INCORRECT", "NOT_ATTEMPTED"]
CHOICE_LETTER_TO_STRING = dict(zip(CHOICE_LETTERS, CHOICE_STRINGS))
DEFAULT_GRADE_IF_UNPARSEABLE = "C" # Corresponds to NOT_ATTEMPTED
````

## 4. 当前状态

截至 2026-06-12，SimpleQA-synth 仍在核验和增补中。预计在一周内完成最终定稿并更新 Hugging Face 数据集版本。

数据集链接：[Hackathon42/SimpleQA-synth](https://huggingface.co/datasets/Hackathon42/SimpleQA-synth/tree/main)。

最新版本：6/12/2026版，有418题。
