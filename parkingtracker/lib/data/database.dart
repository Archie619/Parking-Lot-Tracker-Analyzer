// Opens the app’s SQLite file (parkingtracker.db) and puts it in the app.
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show rootBundle; // Read bundled assets
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart'; // SQLite driver for Flutter

class AppDatabase {
  AppDatabase._();
  static Database? _db;

  // File names/paths
  static const _dbName = 'parkingtracker.db'; // Sandbox file name
  static const _assetDb = 'assets/db/parkingtracker.db'; // Asset
  static const _dbVersion = 1; // Increment this if schema changes

  // Open/create the DB in the app sandbox
  // Copies asset into sandbox on first run
  static Future<Database> open() async {
    if (_db != null) return _db!;

    final dir = await getApplicationDocumentsDirectory();
    // Build the path to db file under data folder
    final dbPath = p.join(dir.path, _dbName);

    debugPrint('DB file -> $dbPath');

    // Ensure a file exists at dbPath
    await _ensureDbExists(dbPath);

    // Opens the database file at dbPath
    _db = await openDatabase(
      dbPath,
      version: _dbVersion, // Database version number
      onConfigure: (db) async {
        // Makes sure every space belongs to a valid lot in lot_summary.
        await db.execute('PRAGMA foreign_keys = ON;');
        // Use WAL mode (writing into parkingtracker.db-wal, SQLite later merges it)
        await db.rawQuery('PRAGMA journal_mode = WAL;');
      },
      // Creates tables/triggers on first run
      onCreate: (db, newVersion) async => _createSchema(db),

      // Rebuilds schema when version number increases
      onUpgrade: (db, oldVersion, newVersion) async => _rebuildSchema(db),

      // After opening, make sure all tables and triggers exist.
      onOpen: (db) async => _createSchema(db),
    );
    // Return the opened database so the app can use it.
    return _db!;
  }

  // Copy the bundled asset into the sandbox if the file isn't there yet.
  static Future<void> _ensureDbExists(String dbPath) async {
    final file = File(dbPath);
    if (await file.exists()) return;

    final bytes = await rootBundle.load(_assetDb);
    await file.writeAsBytes(
      bytes.buffer.asUint8List(bytes.offsetInBytes, bytes.lengthInBytes),
      flush: true,
    );
  }

  // Make sure the proper tables and triggers exist (and create if they're missing).
  static Future<void> _createSchema(DatabaseExecutor ex) async {
    // Lot header (totals for each lot)
    await ex.execute('''
      CREATE TABLE IF NOT EXISTS lot_summary (
        lot_code      TEXT PRIMARY KEY,
        total_spaces  INTEGER NOT NULL,
        occupied      INTEGER NOT NULL DEFAULT 0,
        free          INTEGER NOT NULL DEFAULT 0,
        handicap_     INTEGER NOT NULL DEFAULT 0
      );
    ''');

    // One row per space/spot
    await ex.execute('''
      CREATE TABLE IF NOT EXISTS space (
        space_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        lot_code      TEXT NOT NULL,
        space_number  INTEGER NOT NULL,
        is_occupied   INTEGER NOT NULL DEFAULT 0,
        handicap      INTEGER NOT NULL DEFAULT 0,
        UNIQUE(lot_code, space_number)
      );
    ''');

    // Keep lot_summary.occupied/free in sync when a spot flips occupied
    await ex.execute('''
      CREATE TRIGGER IF NOT EXISTS trg_space_update_totals
      AFTER UPDATE OF is_occupied ON space
      BEGIN
        UPDATE lot_summary
        SET occupied = (SELECT COUNT(*) FROM space s WHERE s.lot_code = NEW.lot_code AND s.is_occupied = 1),
            free     = (SELECT COUNT(*) FROM space s WHERE s.lot_code = NEW.lot_code AND s.is_occupied = 0)
        WHERE lot_code = NEW.lot_code;
      END;
    ''');

    // Keep totals up-to-date when inserting new spaces
    await ex.execute('''
      CREATE TRIGGER IF NOT EXISTS trg_space_insert_totals
      AFTER INSERT ON space
      BEGIN
        UPDATE lot_summary
        SET total_spaces = (SELECT COUNT(*) FROM space s WHERE s.lot_code = NEW.lot_code),
            occupied     = (SELECT COUNT(*) FROM space s WHERE s.lot_code = NEW.lot_code AND s.is_occupied = 1),
            free         = (SELECT COUNT(*) FROM space s WHERE s.lot_code = NEW.lot_code AND s.is_occupied = 0)
        WHERE lot_code = NEW.lot_code;
      END;
    ''');

    // Keep totals up-to-date when deleting spaces
    await ex.execute('''
      CREATE TRIGGER IF NOT EXISTS trg_space_delete_totals
      AFTER DELETE ON space
      BEGIN
        UPDATE lot_summary
        SET total_spaces = (SELECT COUNT(*) FROM space s WHERE s.lot_code = OLD.lot_code),
            occupied     = (SELECT COUNT(*) FROM space s WHERE s.lot_code = OLD.lot_code AND s.is_occupied = 1),
            free         = (SELECT COUNT(*) FROM space s WHERE s.lot_code = OLD.lot_code AND s.is_occupied = 0)
        WHERE lot_code = OLD.lot_code;
      END;
    ''');
  }

  // Rebuilds tables/triggers when schema version changes
  // Called automatically when _dbVersion increases
  static Future<void> _rebuildSchema(Database db) async {
    await db.transaction((txn) async {
      await txn.execute('DROP TRIGGER IF EXISTS trg_space_update_totals;');
      await txn.execute('DROP TRIGGER IF EXISTS trg_space_insert_totals;');
      await txn.execute('DROP TRIGGER IF EXISTS trg_space_delete_totals;');
      await txn.execute('DROP TABLE IF EXISTS space;');
      await txn.execute('DROP TABLE IF EXISTS lot_summary;');
      await _createSchema(txn);
    });
  }

  // Wipe all rows (keeps tables/triggers)
  static Future<void> clearAll() async {
    final db = await open();
    await db.transaction((txn) async {
      await txn.delete('space');
      await txn.delete('lot_summary');
    });
  }

  // Delete the sandbox database file (the writable copy the app uses)
  // Next time the app is restarted the asset is copied again
  static Future<void> nukeDB() async {
    final dir = await getApplicationDocumentsDirectory();
    final path = p.join(dir.path, _dbName);

    await _db?.close();
    _db = null;

    if (await File(path).exists()) {
      await deleteDatabase(path);
    }
  }
}
