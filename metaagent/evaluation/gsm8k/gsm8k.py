# Modified from deepeval, rewritten to prevent the massive dependency and the unnecessary code. 
# TODO: Add a base benchmark class that supports multi modal evaluation.

from typing import List, Optional, Dict
from datasets import load_dataset
import pandas as pd
from tqdm import tqdm

from metaagent.evaluation.golden import Golden
from metaagent.evaluation.gsm8k.template import GSM8KTemplate
from metaagent.evaluation.score import Scorer


class GSM8K:
    def __init__(
        self,
        n_shots: int = 3,
        enable_cot: bool = True,
        n_problems: int = 1319,
        **kwargs,
    ):
        assert n_shots <= 15, "GSM8K only supports n_shots <= 15"
        super().__init__(**kwargs)
        self.scorer = Scorer()
        self.shots_dataset: List[Dict] = None

        self.n_shots: int = n_shots
        self.enable_cot: bool = enable_cot
        self.n_problems: int = n_problems

        self.predictions: Optional[pd.DataFrame] = None
        self.overall_score: Optional[float] = None

    def evaluate(self, agent) -> Dict:
        overall_correct_predictions = 0
        overall_total_predictions = self.n_problems
        predictions_row = []

        # Solving each problem
        goldens = self.load_benchmark_dataset()[: self.n_problems]
        for golden in tqdm(
            goldens, desc=f"Processing {self.n_problems} problems"
        ):
            prediction, score = self.predict(agent, golden).values()
            if score:
                overall_correct_predictions += 1
            predictions_row.append((golden.input, prediction, score))

        # Calculate overall accuracy
        overall_accuracy = (
            overall_correct_predictions / overall_total_predictions
        )
        print(f"Overall GSM8K Accuracy: {overall_accuracy}")

        self.predictions = pd.DataFrame(
            predictions_row, columns=["Input", "Prediction", "Correct"]
        )
        self.overall_score = overall_accuracy

        return overall_accuracy

    def predict(self, agent, golden: Golden) -> Dict:
        # Define prompt template
        assert (
            self.shots_dataset is not None
        ), "Example dataset is empty. Call load_benchmark."
        prompt: dict = GSM8KTemplate.generate_output(
            train_set=self.shots_dataset,
            input=golden.input,
            n_shots=self.n_shots,
            enable_cot=self.enable_cot,
        )

        # Enforced model generation
 
        prompt += "Make sure to output only the numerical answer."
        prediction = agent.generate(prompt)

        score = self.scorer.exact_match_score(
            golden.expected_output, prediction
        )

        return {"prediction": prediction, "score": score}

    def load_benchmark_dataset(self) -> List[Golden]:
        # Load dataset
        dataset = load_dataset("gsm8k", "main", trust_remote_code=True)
        self.dataset = dataset

        # Construct example dataset for n_shot inference
        if not self.shots_dataset:
            train_set = dataset["train"]
            shots_set = []
            for data in train_set:
                shots_set.append(data)
            self.shots_dataset = shots_set

        # Construct test set
        goldens: List[Golden] = []
        for data in dataset["test"]:
            input = data["question"]
            output = GSM8KTemplate.format_answer(data)
            golden = Golden(input=input, expected_output=output)
            goldens.append(golden)

        return goldens
