import 'dart:convert';

import 'package:http/http.dart' as http;

class Requests {
  // List of HTTP GET/POST Requests to communicate with backend endpoints.

  // /lot-status
  Future<Map<String, dynamic>?> fetchLotInfo(String lotName) async {
    // add name of lot to header of request
    final response = await http.get(
      Uri.parse('http://10.0.2.2:8000/lot-preview'),
      headers: {'lot-name': lotName},
    );
    if (response.statusCode == 200) {
      print(jsonDecode(response.body));
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      print(response.statusCode);
      return null;
    }
  }

  // /lot-map
  Future<List<List<dynamic>>?> fetchLotMap(String lotName) async {
    // add name of lot to header of request
    final response = await http.get(
      Uri.parse('http://10.0.2.2:8000/lot-map'),
      headers: {'lot-name': lotName},
    );
    if (response.statusCode == 200) {
      print(jsonDecode(response.body));
      final responseBody = jsonDecode(
        response.body,
      ); // get body of response {lot_name: ... , spot_map: [[{...}, {...}]]}
      return (responseBody['spot_map'] as List)
          .map((row) => row as List<dynamic>)
          .toList(); // return spot map as List<List<dynamic>>
    } else {
      print(response.statusCode);
      return null;
    }
  }
}
