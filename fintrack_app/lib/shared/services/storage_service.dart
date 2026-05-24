import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService extends ChangeNotifier {
  static final StorageService _instance = StorageService._internal();
  static StorageService get instance => _instance;
  
  factory StorageService() {
    return _instance;
  }
  
  StorageService._internal();
  
  late SharedPreferences _prefs;
  
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    notifyListeners();
  }
  
  // Auth Storage
  Future<void> saveAccessToken(String token) async {
    await _prefs.setString('access_token', token);
    notifyListeners();
  }
  
  Future<String?> getAccessToken() async {
    return _prefs.getString('access_token');
  }
  
  Future<void> saveRefreshToken(String token) async {
    await _prefs.setString('refresh_token', token);
    notifyListeners();
  }
  
  Future<String?> getRefreshToken() async {
    return _prefs.getString('refresh_token');
  }
  
  Future<void> saveUserId(String userId) async {
    await _prefs.setString('user_id', userId);
    notifyListeners();
  }
  
  Future<String?> getUserId() async {
    return _prefs.getString('user_id');
  }
  
  Future<void> setLoggedIn(bool value) async {
    await _prefs.setBool('is_logged', value);
    notifyListeners();
  }
  
  Future<bool> isLoggedIn() async {
    return _prefs.getBool('is_logged') ?? false;
  }
  
  // General Storage
  Future<void> setString(String key, String value) async {
    await _prefs.setString(key, value);
    notifyListeners();
  }
  
  Future<String?> getString(String key) async {
    return _prefs.getString(key);
  }
  
  Future<void> setInt(String key, int value) async {
    await _prefs.setInt(key, value);
    notifyListeners();
  }
  
  Future<int?> getInt(String key) async {
    return _prefs.getInt(key);
  }
  
  Future<void> setDouble(String key, double value) async {
    await _prefs.setDouble(key, value);
    notifyListeners();
  }
  
  Future<double?> getDouble(String key) async {
    return _prefs.getDouble(key);
  }
  
  Future<void> setBool(String key, bool value) async {
    await _prefs.setBool(key, value);
    notifyListeners();
  }
  
  Future<bool?> getBool(String key) async {
    return _prefs.getBool(key);
  }
  
  Future<void> remove(String key) async {
    await _prefs.remove(key);
    notifyListeners();
  }
  
  Future<void> clear() async {
    await _prefs.clear();
    notifyListeners();
  }
  
  Future<bool> containsKey(String key) async {
    return _prefs.containsKey(key);
  }
}
