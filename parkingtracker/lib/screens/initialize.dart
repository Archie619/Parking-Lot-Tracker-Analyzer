// Initialize widget that allows adding/initializing new lots
// Screen collects lot details and sends them to the backend.

import 'package:flutter/material.dart';
import 'package:parkingtracker/requests.dart';

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
  static const Color cyan = Color(0xFFA7E7FF);

  // Text controllers
  final _lotNameCtrl = TextEditingController();
  final _rtspCtrl = TextEditingController();

  final Requests requests = Requests();
  String? _statusMsg;

  @override
  void dispose() {
    _lotNameCtrl.dispose();
    _rtspCtrl.dispose();
    super.dispose();
  }

  // Called when the Initialize button is pressed
  Future<void> _onInitializePressed() async {
    final lotName = _lotNameCtrl.text.trim();
    final rtspLink = _rtspCtrl.text.trim();

    if (lotName.isEmpty || rtspLink.isEmpty) {
      setState(() => _statusMsg = 'Please fill out all fields.');
      return;
    }

    final response = await requests.initLot(lotName, rtspLink);
    if (response != null) {
      final status = response['status'];
      var message;
      if (status == 'success') {
        message = 'Successfully initialized lot!';
      } else {
        message = response['message'];
      }
      showDialog(
        context: context,
        barrierDismissible: true,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text(status),
            content: Text(message),
            actions: <Widget>[
              TextButton(
                child: const Text('Okay'),
                onPressed: () {
                  Navigator.of(context).pop();
                },
              ),
            ],
          );
        },
      );
    }
  }

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

          _LabeledField(
            label: 'Lot Name',
            hint: 'e.g. Area 19',
            controller: _lotNameCtrl,
            accent: darkerBlue,
            labelColor: blue,
          ),
          const SizedBox(height: 12),

          _LabeledField(
            label: 'RTSP Link',
            hint: 'e.g. rtsp://camera-feed',
            controller: _rtspCtrl,
            accent: darkerBlue,
            labelColor: blue,
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
              ),
              onPressed: _onInitializePressed,
              child: const Text(
                'Initialize',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
              ),
            ),
          ),

          if (_statusMsg != null) ...[
            const SizedBox(height: 12),
            Text(
              _statusMsg!,
              style: TextStyle(
                color: _statusMsg == 'Saved.' ? Colors.green : Colors.red,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

// Reusable labeled text field
class _LabeledField extends StatelessWidget {
  final String label;
  final String hint;
  final TextEditingController controller;
  final TextInputType? keyboardType;
  final Color accent;
  final Color labelColor;

  const _LabeledField({
    required this.label,
    required this.hint,
    required this.controller,
    required this.accent,
    required this.labelColor,
    this.keyboardType,
  });

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        labelStyle: TextStyle(color: labelColor, fontWeight: FontWeight.w600),
        hintText: hint,
        enabledBorder: OutlineInputBorder(
          borderSide: BorderSide(color: accent, width: 1.25),
          borderRadius: BorderRadius.circular(10),
        ),
        focusedBorder: OutlineInputBorder(
          borderSide: BorderSide(color: accent, width: 1.6),
          borderRadius: BorderRadius.circular(10),
        ),
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 12,
          vertical: 14,
        ),
      ),
    );
  }
}
