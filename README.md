# Identifying Distinctive Features for Explainable Face Verification
IDFEFV is a front end project that aids in the research of Dr. Hand's Machine Perception Lab.

*Steps to run*:
1. git clone https://github.com/taylor-boyd/CS425.git
2. For virtual environments, do **python3 -m venv IDFEFVEnv** or **conda create -n IDFEFVEnv**
3. Activate python environment with **source IDFEFVEnv/bin/activate** or with **conda activate IDFEFVEnv**
4. Install PyTorch (Auto face alignment requires CUDA) https://pytorch.org/. Using conda to install PyTorch installs all dependencies which makes dependency requirements easier to handle.
5. **pip3 install -r requirements.txt**
6. **python3 IDFEFV.py**

*Extra Notes*: <br />
/backend/ contains all the backend functionality, such as the unique feature detection algorithm as well as the face alignment algorithms. 

FaceAlignment.py is the auto face alignment algorithm. <br />
FaceAlignmentv2.py is the manual face alignment.
