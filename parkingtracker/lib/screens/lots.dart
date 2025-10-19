// Lots screen displays all parking lots and their current availability
// Pulled from local SQLite (lot_summary)

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:parkingtracker/screens/lotInfo.dart';
import 'package:parkingtracker/lot.dart';
import '../data/database.dart' as appdb;

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
  // Holds each row from the lot_summary table
  List<Map<String, Object?>> _lots = [];
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _loadLots(); // Loads data immediately when this screen first appears
    _timer = Timer.periodic(
      const Duration(seconds: 30), // Refreshes every 30 seconds
      (_) => _loadLots(),
    );
  }

  @override
  void dispose() {
    _timer?.cancel(); // Stop timer when leaving screen
    super.dispose();
  }

  // Reads the lot_summary table and updates the UI with latest data
  Future<void> _loadLots() async {
    final db = await appdb.AppDatabase.open();
    final rows = await db.query(
      'lot_summary',
      columns: ['lot_code', 'free', 'total_spaces'],
      orderBy: 'lot_code ASC',
    );
    setState(() => _lots = rows);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: _cream, // Page background for this list
      child: ListView.separated(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
        itemCount: _lots.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          final row = _lots[index];
          final title = (row['lot_code'] ?? '').toString();
          final free = row['free']?.toString() ?? '?';
          final total = row['total_spaces']?.toString() ?? '?';
          final subtitle = '$free / $total spots available';

          return _LotCard(
            title: title,
            subtitle: subtitle,
            icon: Icons.local_parking,
            onTap: () {
              // Opens detail page showing map of this specific lot
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => LotsInfoScreen(
                    lot: Lot(lotName: title), // Lot from lib/lot.dart
                  ),
                ),
              );
            },
          );
        },
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
