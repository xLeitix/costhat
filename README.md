# CostHat Proof-of-Concept Implementation

This is a simple, standalone, proof-of-concept implementation of CostHat in
the Python programming language.

**Files:**
* `costhat.py`: contains the actual model
* `costhat_tests.py`: some simple smoke tests and examples
* `ucc_casestudy.py`: case study implementation, uses the application model specified in `ucc_casestudy_model.xml`
* `ucc_eval.py`: evaluation script for scalability of cost evaluation
* `numerical_eval.csv`: raw data resulting from the scalability evaluation
* `generate_plots.py`: helper to generate plots from this raw data using ggplot

**Usage:**

CostHat models can be constructed either via Python program code or in XML.
For examples that construct models in Python please refer to `costhat_tests.py`.
A somewhat large example of an XML-based definition is in `ucc_casestudy_model.xml`,
and `ucc_casestudy.py` shows how to instantiate an XML-based CostHat model in  code.
