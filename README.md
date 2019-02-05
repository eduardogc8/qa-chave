# qa-chave
Question Answering system for Portuguese using Chave collection https://www.linguateca.pt/CHAVE/.

Source code for a simple Question Answering system (QA) for the Portuguese language. 
The dataset used for training e test was the collection Chave.

In the benchmark.ipynb is available the results.

## NER Trained Model
ner.sav: CRF model for Named Entity Recognition (NER) using the entities VALOR, OBJECTO, OBRA, ABSTRACCAO, ACONTECIMENTO, TEMPO, PESSOA, LOCAL, COISA, ORGANIZACAO e OUTRO.

This model was trained using the Harem collection https://www.linguateca.pt/HAREM/.

## Article
https://link.springer.com/chapter/10.1007/978-3-319-99722-3_14

## For Cite:
__Cortes, Eduardo G., Vinicius Woloszyn, and Dante AC Barone. "When, Where, Who, What or Why? A Hybrid Model to Question Answering Systems." International Conference on Computational Processing of the Portuguese Language. Springer, Cham, 2018.__

bibtex:
```
@inproceedings{cortes2018or,
  title={When, Where, Who, What or Why? A Hybrid Model to Question Answering Systems},
  author={Cortes, Eduardo G and Woloszyn, Vinicius and Barone, Dante AC},
  booktitle={International Conference on Computational Processing of the Portuguese Language},
  pages={136--146},
  year={2018},
  organization={Springer}
}
```
