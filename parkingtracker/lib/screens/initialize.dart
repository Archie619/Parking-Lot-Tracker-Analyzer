// Initialize widget that allows adding/initializing new lots
// Screen collects lot details, writes them to SQLite, and can delete lots.

import 'package:flutter/material.dart';
import 'package:sqflite/sqflite.dart' show Sqflite; // For testing DB readback
import '../data/database.dart' as appdb;

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
  static const Color cyan = Color(0xFFA7E7FF); // delete button background

  // Text controllers
  final _lotNameCtrl = TextEditingController();
  final _totalCtrl = TextEditingController();
  final _accessibleCtrl = TextEditingController();

  // Status message
  String? _statusMsg;

  @override
  void dispose() {
    _lotNameCtrl.dispose();
    _totalCtrl.dispose();
    _accessibleCtrl.dispose();
    super.dispose();
  }

  // Input checks before saving
  String? _validate() {
    final name = _lotNameCtrl.text.trim();
    final total = int.tryParse(_totalCtrl.text.trim());
    final acc = int.tryParse(_accessibleCtrl.text.trim());

    if (name.isEmpty) return 'Please enter a lot name.';
    if (total == null || total <= 0) return 'Enter a valid total space count.';
    if (acc == null || acc < 0) return 'Enter a valid accessible space count.';
    if (acc > total) return 'Accessible spaces cannot exceed total spaces.';
    return null;
  }

  // Called when the Initialize button is pressed. Checks that all fields are valid and saves the lot to SQLite.
  Future<void> _onInitializePressed() async {
    final err = _validate();
    if (err != null) {
      setState(() => _statusMsg = err);
      return;
    }

    final lot = _lotNameCtrl.text.trim();
    final total = int.parse(_totalCtrl.text.trim());
    final acc = int.parse(_accessibleCtrl.text.trim());

    try {
      final db = await appdb.AppDatabase.open();

      await db.transaction((txn) async {
        // Remove any existing rows for this lot
        await txn.delete('space', where: 'lot_code = ?', whereArgs: [lot]);
        await txn.delete(
          'lot_summary',
          where: 'lot_code = ?',
          whereArgs: [lot],
        );

        // Insert lot summary row
        await txn.insert('lot_summary', {
          'lot_code': lot,
          'total_spaces': total,
          'occupied': 0,
          'free': total,
          'handicap_': acc,
        });

        // Insert all spaces for this lot
        final batch = txn.batch();
        for (var n = 1; n <= total; n++) {
          batch.insert('space', {
            'lot_code': lot,
            'space_number': n,
            'is_occupied': 0,
            'handicap': n <= acc ? 1 : 0,
          });
        }
        await batch.commit(noResult: true);
      });

      // (Test for DB readback)
      await _debugPrintLot(lot);

      setState(() => _statusMsg = 'Saved.');
    } catch (e) {
      setState(() => _statusMsg = 'Failed to save: $e');
    }
  }

  // Testing to see if database is taking in information after Initializing
  // TODO: Remove after verifying saves in the emulator.
  Future<void> _debugPrintLot(String lot) async {
    final db = await appdb.AppDatabase.open();
    final header = await db.query(
      'lot_summary',
      where: 'lot_code=?',
      whereArgs: [lot],
      limit: 1,
    );
    final spaces =
        Sqflite.firstIntValue(
          await db.rawQuery('SELECT COUNT(*) FROM space WHERE lot_code=?', [
            lot,
          ]),
        ) ??
        0;
    debugPrint('lot_summary row: $header');
    debugPrint('space rows for $lot: $spaces');
  }

  // Deletes one specific lot
  Future<void> _deleteLot(String lot) async {
    final db = await appdb.AppDatabase.open();
    await db.transaction((txn) async {
      await txn.delete('space', where: 'lot_code = ?', whereArgs: [lot]);
      await txn.delete('lot_summary', where: 'lot_code = ?', whereArgs: [lot]);
    });
  }

  // Deletes every lot
  Future<void> _deleteAllLots() async {
    final db = await appdb.AppDatabase.open();
    await db.transaction((txn) async {
      await txn.delete('space');
      await txn.delete('lot_summary');
    });
  }

  // Fetch lot codes for picker
  Future<List<String>> _getLotCodes() async {
    final db = await appdb.AppDatabase.open();
    final rows = await db.query(
      'lot_summary',
      columns: ['lot_code'],
      orderBy: 'lot_code',
    );
    return rows.map((r) => (r['lot_code'] as String)).toList();
  }

  // Delete dialog (select one or delete all)
  Future<void> _showDeleteDialog() async {
    final lots = await _getLotCodes();
    if (lots.isEmpty) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('No lots to delete')));
      return;
    }

    String selected = lots.first;

    await showDialog<void>(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setLocal) {
            return AlertDialog(
              title: const Text('Delete lots'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text('Select one to delete'),
                  ),
                  const SizedBox(height: 8),
                  DropdownButton<String>(
                    isExpanded: true,
                    value: selected,
                    items: lots
                        .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                        .toList(),
                    onChanged: (v) => setLocal(() => selected = v ?? selected),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () async {
                    await _deleteAllLots();
                    if (!mounted) return;
                    Navigator.pop(ctx);
                    setState(() => _statusMsg = 'Deleted all lots.');
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Deleted all lots')),
                    );
                  },
                  child: const Text('Delete all'),
                ),
                TextButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () async {
                    await _deleteLot(selected);
                    if (!mounted) return;
                    Navigator.pop(ctx);
                    setState(() => _statusMsg = 'Deleted "$selected".');
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Deleted "$selected"')),
                    );
                  },
                  child: const Text('Delete selected'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  // Build UI for Initialize screen
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cream,
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
        children: [
          // Page heading
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

          // Lot name input
          _LabeledField(
            label: 'Lot Name',
            hint: 'e.g. Area 19',
            controller: _lotNameCtrl,
            accent: darkerBlue,
            labelColor: blue,
          ),
          const SizedBox(height: 12),

          // Total spaces input
          _LabeledField(
            label: 'Total Spaces',
            hint: 'e.g. 120',
            controller: _totalCtrl,
            keyboardType: TextInputType.number,
            accent: darkerBlue,
            labelColor: blue,
          ),
          const SizedBox(height: 12),

          // Accessible spaces input
          _LabeledField(
            label: 'Accessible Spaces',
            hint: 'e.g. 10',
            controller: _accessibleCtrl,
            keyboardType: TextInputType.number,
            accent: darkerBlue,
            labelColor: blue,
          ),
          const SizedBox(height: 20),

          // Initialize button
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
              // Handles what happens when the "Initialize" button is pressed.
              // It validates the input and saves the new lot to the database.
              onPressed: _onInitializePressed,
              child: const Text(
                'Initialize',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
              ),
            ),
          ),

          const SizedBox(height: 12),

          // Delete button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: cyan,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              onPressed: _showDeleteDialog,
              child: const Text(
                'Delete',
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
