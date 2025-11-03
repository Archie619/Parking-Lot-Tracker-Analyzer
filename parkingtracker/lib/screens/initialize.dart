// Initialize widget that allows adding/initializing new lots
// Screen collects lot details and sends them to the backend.

import 'package:flutter/material.dart';
import 'package:parkingtracker/requests.dart';

// Stateful = Mutable
class InitializeScreen extends StatefulWidget {
  const InitializeScreen({super.key});

  @override
  State<InitializeScreen> createState() => _InitializeScreenState();
}

class _InitializeScreenState extends State<InitializeScreen> {
  // Color palette
  static const Color blue = Color(0xFF5BA8FF);
  static const Color darkerBlue = Color(0xFF3F90F0);
  static const Color cream = Color(0xFFFFFFDF);

  // Create text controllers to retrieve current values of text fields
  final lotNameController = TextEditingController();
  final rtspLinkController = TextEditingController();

  final Requests requests = Requests();
  String? _statusMsg;

  @override
  void dispose() {
    lotNameController.dispose();
    rtspLinkController.dispose();
    super.dispose();
  }

  // Initialize lot function, called when button pressed - pull data from both text fields, then call initLot with data.
  void initializeLot() async {
    final lotName = lotNameController.text.trim();
    final rtspLink = rtspLinkController.text.trim();

    if (lotName.isEmpty || rtspLink.isEmpty) {
      setState(() => _statusMsg = 'Please fill out all fields.');
      return;
    }

    // Check that RTSP link format is valid
    if (!rtspLink.startsWith('rtsp://')) {
      setState(() => _statusMsg = 'RTSP link must start with rtsp://');
      return;
    }

    final response = await requests.initLot(lotName, rtspLink);
    if (response != null) {
      final status = response['status'];
      final message = status == 'success'
          ? 'Successfully initialized lot!'
          : response['message'];

      // Show popup giving status/message of response
      showDialog(
        context: context,
        barrierDismissible: true,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text(status), // wrap strings in text widget to display them.
            content: Text(message),
            actions: <Widget>[
              TextButton(
                child: const Text('Okay'),
                onPressed: () => Navigator.of(context).pop(),
              ),
            ],
          );
        },
      );
    }
  }

  // Build methods called anytime Flutter rebuilds UI, returns Widget
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
        children: [
          const Text(
            'Initialize a Lot',
            style: TextStyle(
              fontFamily: 'Merriweather',
              fontSize: 20,
              fontWeight: FontWeight.w800,
              color: blue,
            ),
          ),
          const SizedBox(height: 12),

          TextField(
            controller: lotNameController,
            decoration: InputDecoration(
              labelText: 'Lot Name',
              hintText: 'e.g. Area 19',
              labelStyle: const TextStyle(
                color: blue,
                fontWeight: FontWeight.w600,
                fontFamily: 'Merriweather',
              ),
              enabledBorder: OutlineInputBorder(
                borderSide: BorderSide(color: darkerBlue, width: 1.25),
                borderRadius: BorderRadius.circular(10),
              ),
              focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(color: darkerBlue, width: 1.6),
                borderRadius: BorderRadius.circular(10),
              ),
              filled: true,
              fillColor: Colors.white,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 14,
              ),
            ),
          ),
          const SizedBox(height: 12),

          TextField(
            controller: rtspLinkController,
            decoration: InputDecoration(
              labelText: 'RTSP Link',
              hintText: 'e.g. rtsp://camera-feed',
              labelStyle: const TextStyle(
                color: blue,
                fontWeight: FontWeight.w600,
                fontFamily: 'Merriweather',
              ),
              enabledBorder: OutlineInputBorder(
                borderSide: BorderSide(color: darkerBlue, width: 1.25),
                borderRadius: BorderRadius.circular(10),
              ),
              focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(color: darkerBlue, width: 1.6),
                borderRadius: BorderRadius.circular(10),
              ),
              filled: true,
              fillColor: Colors.white,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 14,
              ),
            ),
          ),
          const SizedBox(height: 20),

          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
                textStyle: const TextStyle(
                  fontFamily: 'Merriweather',
                  fontWeight: FontWeight.w700,
                ),
              ),
              onPressed: initializeLot,
              child: const Text('Initialize'),
            ),
          ),

          if (_statusMsg != null) ...[
            const SizedBox(height: 12),
            Text(
              _statusMsg!,
              style: TextStyle(
                color: _statusMsg == 'Saved.' ? Colors.green : Colors.red,
                fontWeight: FontWeight.w500,
                fontFamily: 'Merriweather',
              ),
            ),
          ],
        ],
      ),
    );
  }
}
