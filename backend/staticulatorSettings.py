class StaticulatorSettings:

    def __init__(self):
        self.zone_names = ["Blue Goalie", "Blue Two-Man Rod", "Red Three-Man Rod", "Blue Five-Man Rod",
                           "Red Five-Man Rod", "Blue Three-Man Rod", "Red Two-Man Rod", "Red Goalie"]

        p = {
            "r": {
                1: ["Jasper Cillessen"],
                2: ["Memphis Depai", "Wesley Sneijder"],
                3: ["Arjen Robben", "Dennis Bergkamp", "Klaas-Jan Huntelaar"],
                5: ["Robin van Persie", "Tim Krul", "Johan Cruijff (14)", "Louis van Gaal", "Johan Derksen"],
            },
            "b": {
                1: ["Rom Langerak"],
                2: ["Max Pijnappel", "Andrea Continella"],
                3: ["Lionel Messi", "Christiano Ronaldo", "Ronaldinho"],
                5: ["Hein Huijskes", "Iris ten Klooster", "Mathijs Vogelezang", "Melle Ploeg", "Sophie Takken"],
            },
        }
        self.players = [
            p["b"][1], p["b"][2], p["r"][3], p["b"][5],
            p["r"][5], p["b"][3], p["r"][2], p["r"][1],
            [["Rahul Dravid"]] * 5  # Incorrect player list with fake players
        ]
