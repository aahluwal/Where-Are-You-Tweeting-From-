import model
import data
import feature_selection
from data import cities

def update_features_in_db(cities):
    for city in cities:
	feature_selection.populate_db_with_features(city)
	print "Finished a city!"
def main():
    update_features_in_db(cities)


if __name__ == "__main__":
    main()
