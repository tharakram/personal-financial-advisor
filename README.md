## Personal Financial Advisor

#### Pre-requisites
- Python 3.10+
- Pip
- Virtualenv
- install the dependencies: `pip install -r requirements.txt`
- Request Nvidia LLM API Key from [here](https://build.nvidia.com/nvidia/embed-qa-4?snippet_tab=Python)
- Generate fake statements using `bank_fake_statement_generator.py` & `cc_fake_statement_generator.py`

#### Setup & Run
- Create a virtual environment and activate it
- `python -m pip install -r requirements.txt`
- Create a .env file in the root directory of the project
- Add the following line to the.env file: `NVIDIA_API_KEY=<YOUR_API_KEY>`
- Run the app using the command below: `chainlit run app.py -w`



![alt text](assets/image.png)