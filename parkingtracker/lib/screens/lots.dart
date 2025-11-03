// Lots screen displays all parking lots and their current availability
// Pulled from backend via requests.dart

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:parkingtracker/screens/lotInfo.dart';
import 'package:parkingtracker/lot.dart';
import 'package:parkingtracker/requests.dart';

// Color palette
const _blue = Color(0xFF5BA8FF);
const _badgeBg = Color(0xFFA7E7FF);
const _cardBg = Color(0xFFFFF9E6);
const _cardBorder = Color(0xFFF1E7B8);
const _cream = Color(0xFFFFFFDF);

// Stateful = Mutable
class LotsScreen extends StatefulWidget {
  const LotsScreen({super.key});

  @override
  State<LotsScreen> createState() => _LotsScreenState();
}

class _LotsScreenState extends State<LotsScreen> {
  final Requests requests =
      Requests(); // Create Requests object to call functions to get data
  late Timer timer; // Will be destroyed when widget is dismissed.

  // Get list of lot names from backend, display them in list
  List<Lot> lots = [];

  // Tracks which sort mode is active (availability or size)
  bool _sortByAvailability = true;

  Future<void> loadLots() async {
    final names = await requests.fetchLotNames();
    if (names != null) {
      lots = names.map((name) => Lot(lotName: name)).toList();
    }
  }

  // Initial state of widget: get lot data for each info, and then update periodically from there.
  @override
  void initState() {
    super.initState();
    loadLots().then((_) {
      setState(() {});
      updateLotData();
    });

    // Every 60 seconds, refresh data
    timer = Timer.periodic(
      const Duration(seconds: 30),
      (timer) => updateLotData(),
    );
  }

  // Cancel timer
  @override
  void dispose() {
    timer.cancel();
    super.dispose();
  }

  // For each lot, get data from backend on how many spots available & then update UI.
  Future<void> updateLotData() async {
    for (Lot lot in lots) {
      final data = await requests.fetchLotInfo(lot.lotName);

      if (data != null) {
        setState(() {
          // Updates UI
          // Update lot data
          lot.availableSpots = data['available_spots'];
          lot.totalSpots = data['total_spots'];
        });
      }
    }
    // After updating all lots, reapply current sort mode
    _sortLots();
  }

  // Sorts the lots by either availability (free spaces) or total size
  void _sortLots() {
    setState(() {
      if (_sortByAvailability) {
        lots.sort(
          (a, b) => (b.availableSpots ?? 0).compareTo(a.availableSpots ?? 0),
        );
      } else {
        lots.sort((a, b) => (b.totalSpots ?? 0).compareTo(a.totalSpots ?? 0));
      }
      _sortByAvailability = !_sortByAvailability; // toggles the next sort mode
    });
  }

  // Build methods called anytime Flutter rebuilds UI, returns Widget
  @override
  Widget build(BuildContext context) {
    return Container(
      color: _cream, // Page background for this list
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header row and sort button
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Parking Lots',
                  style: TextStyle(
                    fontFamily: 'Merriweather',
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                    color: _blue,
                  ),
                ),
                ElevatedButton(
                  onPressed: _sortLots,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _blue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 10,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: Text(
                    _sortByAvailability
                        ? 'Sort by Size'
                        : 'Sort by Availability',
                    style: const TextStyle(
                      fontFamily: 'Merriweather',
                      fontWeight: FontWeight.w700,
                      fontSize: 13.5,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // List of parking lots
            Expanded(
              child: ListView.separated(
                itemCount: lots.length,
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final lot = lots[index];
                  final title = lot.lotName;
                  final free = lot.availableSpots?.toString() ?? '?';
                  final total = lot.totalSpots?.toString() ?? '?';
                  final subtitle = '$free / $total spots available';

                  return _LotCard(
                    title: title,
                    subtitle: subtitle,
                    icon: Icons.local_parking,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => LotsInfoScreen(
                            lot: lot, // Pass full lot object
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Reusable card widget for displaying each lot’s info row
class _LotCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final VoidCallback? onTap;

  const _LotCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0.5,
      color: _cardBg,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: const BorderSide(color: _cardBorder, width: 1),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap:
            onTap ??
            () => ScaffoldMessenger.of(
              context,
            ).showSnackBar(SnackBar(content: Text('$title tapped'))),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
          child: Row(
            children: [
              // Badge with the P icon
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: _badgeBg,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: _blue),
              ),
              const SizedBox(width: 12),

              // Title (lot name) and subtitle (# of spaces)
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title
                    Text(
                      title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'Merriweather',
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                        color: _blue,
                      ),
                    ),
                    const SizedBox(height: 2),

                    // Subtitle
                    Text(
                      subtitle,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'Merriweather',
                        fontSize: 13,
                        color: _blue,
                        height: 1.2,
                      ),
                    ),
                  ],
                ),
              ),

              // Chevron icon
              const Icon(Icons.chevron_right, color: _blue),
            ],
          ),
        ),
      ),
    );
  }
}
