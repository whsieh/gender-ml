# gender-ml
A super-simple API that attempts to map first name to the binary gender (male or female) _most commonly associated with that name_. Yes, I realize there are genders beyond male and female. Unfortunately, it's nigh impossible to accurately classify them based only on first name, so this service (as of now) sticks to distinguishing between male and female.

This API is not designed to magically pinpoint a user's actual gender based only on one's first name. It is better used when the impact of occasional errors is insignificant, such as approximating the gender composition of a group of people when only the first name is known.

An authenticated-ish version of this code is currently being employed in an iOS app I'm making called [Couplr](http://www.couplr.co), where I am using it as a heuristic to find potential romantic pairings in social networks. Keep in mind that this version, located at `gender-ml.herokuapp.com`, is free to use, and does not have any sort of explicit request limit.

## Usage:

`GET http://gender-ml.herokuapp.com/classify?names=ada,grace,anita,guido,dennis,steve`

The response will be a JSON object of the form:

`{"grace": 1, "guido": 0, "ada": 1, "anita": 1, "dennis": 0, "steve": 0}`

where `0` represents male, `1` represents female, and `2` represents undetermined.

## How it works:

This service uses a linear SVM to predict gender given only a first name. It does this by breaking the name down into 2- and 3-grams formed by the letters in the name (special beginning-of-name and end-of-name characters are inserted marking the beginning and end of the name). While this strategy predicts most (about 90% using 10-fold cross validation) of the names correctly, some names are predicted incorrectly or are very close to the decision boundary. Thus, the classifier (in production) first attempts to look for a given name in a table of misclassified names and returns early if it finds the name there. Otherwise, it extracts ngram features from the name and computes the distance of the name to the separating hyperplane. If this distance is too small, it will classify the name as `2`, which indicates "undetermined".

A word of warning: in its current state, this classifier is not built to detect androgynous names, and will (for instance) classify names such as "Sam" as male, and "Nicky" as female.
