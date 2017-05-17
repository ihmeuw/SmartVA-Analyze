# Changelog 1.2

### Algorithm
* Add option to ignore AIDS predictions in regions with low HIV prevalence
* Change the causes aggregation on the adult cause list. Specifically:
    * Other Cancers is no longer aggregated into Other NCDs
    * Congestive Heart Failure is no longer aggregated into Other CVD
    * Congestive Heart Failure and Acute Myocaridal Infarction are aggregated
      into Ischemic Heart Disease
    * Asthma and COPD are aggregated into Chroic Respiratory Disease
    * Epilepsy is aggregated into Other Non-communicable Diseases
* Add logic rules to predict cases where the endorsement of key symptoms
  definitively leads to a certain prediction.
* Add logic rule requiring the endorsement of key symptoms for causes. Without
  these endorsements tariff ignores the cause regardless of the score or rank.
* Add logic rules for diagnostic rule-outs. Some key symptoms are enough to say
  a certain cause cannot be underlying cause of death. Tariff ignores these
  causes regardless of the score or rank.
* The minimum tariff score required for a cause to be considered a valid
  prediction is now cause specific.
* Remove tariffs for symptoms which have no clinical significance. These are
  artifacts of small number of gold standards for certain causes. Most of these
  are words said in the open response which do not generalize to other
  populations.

### Data Validation
* Verifies interviewee consented to survey and removes non-consenting
  observations.
* Increased verification of age values. Observations without valid ages are now
  removed from the data before estimation.

### User Experience
* Add warnings for errors in input data.
* Add progress bar and estimated time remain for each step.
* Add option to turn off generation of figures.
* Move common options for Health Care Experience (HCE) and Freetext questions
  from main console to options drop down menu.
* Add command line interface which enhances usability for automated systems.

### Technical Improvements
* Robust to errors in input data. The app no longer stalls when the input data
  is missing columns.
* Increased computational performance with threads.
* Separate model logic from GUI logic to increase code maintainability.
* Separate functional logic from data values to promote testability and ease
  customizability.
* Add test suite.
