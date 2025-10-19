// Admin login screen shown before accessing Initialize
import 'package:flutter/material.dart';

const adminPassword = '4020'; // App password

// Stateful = Mutable
class AdminLogin extends StatefulWidget {
  const AdminLogin({super.key});

  @override
  State<AdminLogin> createState() => _AdminLoginState();
}

class _AdminLoginState extends State<AdminLogin> {
  final _passCtrl = TextEditingController();
  bool _showError = false;
  bool _obscure = true; // Show/hide password toggle

  // Palette
  static const blue = Color(0xFF5BA8FF); // Text/icons
  static const darker = Color(0xFF3F90F0); // Title text
  static const cream = Color(0xFFFFFFDF); // Page background
  static const barBg = Color(0xFF8FD6FF); // AppBar background
  static const btnBg = Color(0xFFFFF9E6); // Pale yellow buttons
  static const panelBg = Color(0xFFEAF6FF); // Pale blue panel
  static const yellow = Color(0xFFFFE79B); // Header strip + section band

  @override
  void dispose() {
    _passCtrl.dispose();
    super.dispose();
  }

  // Checks password
  void _tryLogin() {
    if (_passCtrl.text.trim() == adminPassword) {
      Navigator.pop(context, true); // Success
    } else {
      setState(() => _showError = true); // Show error message
    }
  }

  // Build method called anytime Flutter rebuilds UI
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,

      // Top app bar
      appBar: AppBar(
        backgroundColor: barBg,
        iconTheme: const IconThemeData(color: blue),
        centerTitle: true,
        title: const Text(
          'Parking Lot Tracker',
          style: TextStyle(
            fontFamily: 'Merriweather',
            fontSize: 32,
            fontWeight: FontWeight.w800,
            color: darker,
          ),
        ),
      ),

      body: Column(
        children: [
          // Yellow strip
          Container(height: 8, width: double.infinity, color: yellow),

          // Header bar with title text ("Admin Login")
          Container(
            height: 32,
            width: double.infinity,
            color: yellow,
            alignment: Alignment.center,
            child: const Text(
              'Admin Login',
              style: TextStyle(
                fontFamily: 'Merriweather',
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: blue,
              ),
            ),
          ),

          // Login form panel
          Expanded(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 420),
                child: Card(
                  elevation: 2,
                  color: panelBg, // Panel background
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                            'Admin Password',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              color: blue,
                              fontFamily: 'Merriweather',
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),

                        // Password field with visibility toggle
                        TextField(
                          controller: _passCtrl,
                          obscureText: _obscure,
                          style: const TextStyle(
                            color: blue,
                            fontFamily: 'Merriweather',
                          ),
                          decoration: InputDecoration(
                            filled: true,
                            fillColor:
                                Colors.white, // Inner box to fill in password
                            hintText: 'Enter password',
                            hintStyle: const TextStyle(
                              color: blue,
                              fontFamily: 'Merriweather',
                            ),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: const BorderSide(
                                color: blue,
                                width: 1.5,
                              ),
                            ),
                            // Eye icon to toggle password visibility
                            suffixIcon: IconButton(
                              icon: Icon(
                                _obscure
                                    ? Icons.visibility_off
                                    : Icons.visibility,
                                color: blue,
                              ),
                              onPressed: () =>
                                  setState(() => _obscure = !_obscure),
                            ),
                          ),
                          onSubmitted: (_) => _tryLogin(),
                        ),

                        // Error message
                        if (_showError) ...[
                          const SizedBox(height: 8),
                          const Text(
                            'Incorrect password.',
                            style: TextStyle(
                              color: Colors.red,
                              fontFamily: 'Merriweather',
                            ),
                          ),
                        ],

                        const SizedBox(height: 20),

                        // Unlock and Cancel buttons
                        Row(
                          children: [
                            Expanded(
                              child: ElevatedButton(
                                onPressed: _tryLogin,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: btnBg,
                                  foregroundColor: blue,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  elevation: 0,
                                  textStyle: const TextStyle(
                                    fontFamily: 'Merriweather',
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                child: const Text('Unlock'),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: ElevatedButton(
                                onPressed: () => Navigator.pop(context, false),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: btnBg,
                                  foregroundColor: blue,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  elevation: 0,
                                  textStyle: const TextStyle(
                                    fontFamily: 'Merriweather',
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                child: const Text('Cancel'),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
