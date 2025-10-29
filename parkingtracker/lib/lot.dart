class Lot {
  // Required
  String lotName;
  // Will be updated with backend
  int? availableSpots;
  int? totalSpots;
  List<List<dynamic>>? lotMap;

  Lot({required this.lotName, this.availableSpots, this.totalSpots, this.lotMap});

}