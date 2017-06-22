# Changelog 2.0

* Refactor implementation of tariff for increased performance (PR140)
* Add new output file with multiple predictions, qualitative likelihood
  associated with each predicition, and descriptions of endorsed symptoms as
  both an xlsx with formatting and as a machine-readable csv (PR143, PR145)
* Censor stillbirth if age is greater than zero days (PR144)
* Remove the condition "Mother was told she had HIV by health worker" from
  child AIDS rule (PR148)
