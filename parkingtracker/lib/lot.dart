class Lot {

  String lotName;
  int lotNumber;
  int spotsTaken;
  int totalSpots;
  String mapPath; // path to map image

  Lot(this.lotName, this.lotNumber, this.spotsTaken, this.totalSpots, this.mapPath);

  int get availableSpots => totalSpots - spotsTaken;

}