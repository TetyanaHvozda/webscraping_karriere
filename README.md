# webscraping_karriere
Automating job search in Python

Downgrade Python version using Virtual Environments 
```bash
python3 --version 
virtualenv -p python3.12 myenv 
source myenv/bin/activate 
pip install numpy scipy 
pip install mysql-connector-python
pip install pandas
pip install scikit-learn 
pip install pdfplumber 
python job_matching.py 
deactivate
```
While running job_matching.py make sure you have cv.pdf file in your folder

### Video Tutorials

Here are some helpful tutorials to guide you through the process:

1. [Web scraping jobs Part 1: extract a list of jobs](https://youtu.be/oCR23dxyrKQ)
2. [Web scraping jobs Part 2: extract job's description](https://youtu.be/bgEWYEijF5s)
3. [Web scraping jobs Part 3: extract job's skills](https://youtu.be/6pLSVMhOPCI)
4. [Web scraping jobs Part 4: cleaning data](https://youtu.be/WBziZ1ufCtA)
5. [Web scraping jobs Part 5: MySQL database connection](https://youtu.be/ZPzW8v8jCV4)
6. [Web scraping jobs Part 6: job matching using cosine similarity](https://youtu.be/PI179cWrcfo)

![Job Scraping Process](./thumbnail.png)