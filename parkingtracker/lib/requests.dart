import 'dart:convert';

import 'package:http/http.dart' as http;

class Requests {

  // List of HTTP GET/POST Requests to communicate with backend endpoints.

  Future<Map<String, dynamic>?> fetchLotInfo(String lotName) async {
    // add name of lot to header of request
    final response = await http.get(Uri.parse(''));

    if (response.statusCode == 200) {
      print(jsonDecode(response.body));
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      print("Failed to load data.");
      return null;
    }
  }

}