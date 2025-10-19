// Main navigation screen for the Parking Lot Tracker app.
// Switches between the "Lots" and "Initialize" pages.
// Main widget that will hold our other widgets.

import 'package:flutter/material.dart';
import 'package:parkingtracker/screens/initialize.dart';
import 'package:parkingtracker/screens/lots.dart';
import 'package:parkingtracker/screens/admin_login.dart';

class Screen extends StatefulWidget {
  const Screen({super.key});

  // Build methods called anytime Flutter rebuilds UI, returns Widget
  @override
  State<Screen> createState() => _ScreenState();
}

class _ScreenState extends State<Screen> {
  // Stateful logic here (things that change)
  int currentPageIndex = 0;
  bool _initUnlocked = false;

  // Color palette
  static const Color _yellow = Color(0xFFFFE79B);
  static const Color _barBg = Color(0xFF8FD6FF);
  static const Color _title = Color(0xFF3F90F0);
  static const Color _blue = Color(0xFF5BA8FF);
  static const Color _cream = Color(0xFFFFFFDF);

  @override
  Widget build(BuildContext context) {
    // Two main pages controlled by bottom navigation
    final pages = <Widget>[const LotsScreen(), const InitializeScreen()];
    // Title above content switches with selected tab
    final sectionTitle = currentPageIndex == 0 ? 'Lots' : 'Initialize';

    return Scaffold(
      appBar: AppBar(
        backgroundColor: _barBg,
        centerTitle: true,
        title: const Text(
          'Parking Lot Tracker',
          style: TextStyle(
            fontFamily: 'Merriweather',
            fontSize: 32,
            fontWeight: FontWeight.w800,
            color: _title,
          ),
        ),
        actions: [
          // Lock button
          IconButton(
            tooltip: 'Lock Initialize',
            icon: const Icon(Icons.lock_outline, color: _title),
            onPressed: () {
              // Relock Initialize page (unlock goes back to false)
              setState(() => _initUnlocked = false);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Admin locked. Initialize now requires login.'),
                ),
              );
            },
          ),
        ],
      ),
      // Main content of the screen
      body: Container(
        color: _cream,
        child: Column(
          children: [
            // Thin yellow divider strip under the AppBar
            Container(height: 8, width: double.infinity, color: _yellow),

            // Yellow title band showing the current section name
            SizedBox(
              width: double.infinity,
              height: 32,
              child: ColoredBox(
                color: _yellow,
                child: Center(
                  child: Text(
                    sectionTitle,
                    style: const TextStyle(
                      fontFamily: 'Merriweather',
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: _blue,
                    ),
                  ),
                ),
              ),
            ),

            // Displays whichever screen is currently selected
            Expanded(child: pages[currentPageIndex]),
          ],
        ),
      ),
      // Bottom navigation bar to switch between "Lots" and "Initialize"
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentPageIndex,
        onDestinationSelected: (int index) async {
          // If user taps "Initialize" but it’s locked, open admin login first
          if (index == 1 && !_initUnlocked) {
            final ok = await Navigator.of(
              context,
            ).push<bool>(MaterialPageRoute(builder: (_) => const AdminLogin()));
            // If login successful, unlock and open Initialize page
            if (ok == true) {
              setState(() {
                _initUnlocked = true;
                currentPageIndex = 1;
              });
              return;
            }
            return;
          }
          // If Initialize is already unlocked or Lots is selected, switch normally
          setState(() => currentPageIndex = index);
        },
        destinations: const <Widget>[
          NavigationDestination(
            selectedIcon: Icon(Icons.map),
            icon: Icon(Icons.map_outlined),
            label: 'Lots',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.perm_data_setting),
            icon: Icon(Icons.perm_data_setting_outlined),
            label: 'Initialize',
          ),
        ],
      ),
    );
  }
}
