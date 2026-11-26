
import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart' as fb;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:google_sign_in/google_sign_in.dart';

class FirebaseAuthService extends FletService {
  FirebaseAuthService({required super.control});

  Future<void>? _initialization;

  FirebaseFirestore get _db => FirebaseFirestore.instance;

  static const String _serverClientId =
      '280226723716-4pi2vpbrl1fp8gomnjmklgllo3s5s04m.apps.googleusercontent.com';

  @override
  void init() {
    super.init();
    control.addInvokeMethodListener(_onInvokeMethod);
    _ensureInitialized();
  }

  Future<void> _ensureInitialized() {
    return _initialization ??= _initializeFirebase();
  }

  Future<void> _initializeFirebase() async {
    if (Firebase.apps.isEmpty) {
      await Firebase.initializeApp();
    }

    await GoogleSignIn.instance.initialize(
      serverClientId: _serverClientId,
    );

    debugPrint('VibeGram: Firebase initialized');
  }

  fb.User get _user {
    final user = fb.FirebaseAuth.instance.currentUser;

    if (user == null) {
      throw Exception('User is not authenticated');
    }

    return user;
  }

  Map<String, dynamic> _args(dynamic args) {
    if (args is Map) {
      return Map<String, dynamic>.from(args);
    }
    return {};
  }

  dynamic _clean(dynamic value) {
    if (value is Timestamp) {
      return value.toDate().toIso8601String();
    }

    if (value is DateTime) {
      return value.toIso8601String();
    }

    if (value is Map) {
      return value.map(
        (key, value) => MapEntry(key.toString(), _clean(value)),
      );
    }

    if (value is List) {
      return value.map(_clean).toList();
    }

    return value;
  }

  Map<String, dynamic> _document(
    DocumentSnapshot<Map<String, dynamic>> snapshot,
  ) {
    return {
      'id': snapshot.id,
      ..._clean(snapshot.data() ?? {}) as Map<String, dynamic>,
    };
  }

  Map<String, dynamic> _userData(fb.User user) {
    return {
      'success': true,
      'authenticated': true,
      'uid': user.uid,
      'email': user.email ?? '',
      'displayName': user.displayName ?? '',
      'photoURL': user.photoURL ?? '',
    };
  }

  Future<void> _ensureUserDocument(fb.User user) async {
    final ref = _db.collection('users').doc(user.uid);
    final snapshot = await ref.get();

    final data = <String, dynamic>{
      'uid': user.uid,
      'email': user.email ?? '',
      'displayName': user.displayName ?? '',
      'avatarUrl': user.photoURL ?? '',
      'updatedAt': FieldValue.serverTimestamp(),
    };

    if (!snapshot.exists) {
      data.addAll({
        'username': '',
        'usernameLower': '',
        'about': '',
        'backgroundUrl': '',
        'createdAt': FieldValue.serverTimestamp(),
      });
    }

    await ref.set(data, SetOptions(merge: true));

    final publicRef = _db.collection('public_users').doc(user.uid);
    final publicSnapshot = await publicRef.get();

    if (!publicSnapshot.exists) {
      await publicRef.set({
        'uid': user.uid,
        'displayName': user.displayName ?? '',
        'avatarUrl': user.photoURL ?? '',
        'username': '',
        'usernameLower': '',
        'createdAt': FieldValue.serverTimestamp(),
      });
    }
  }

  // ==========================================
  // PROFILE
  // ==========================================

  Future<Map<String, dynamic>> _getUserProfile() async {
    final user = _user;

    await _ensureUserDocument(user);

    final snapshot = await _db
        .collection('users')
        .doc(user.uid)
        .get();

    return {
      'success': true,
      'profile': _clean(snapshot.data() ?? {}),
    };
  }

  Future<Map<String, dynamic>> _saveUserProfile(
    Map<String, dynamic> profile,
  ) async {
    final user = _user;

    final username = (profile['username'] ?? '')
        .toString()
        .trim()
        .replaceFirst(RegExp(r'^@'), '')
        .toLowerCase();

    final displayName =
        (profile['displayName'] ?? '').toString().trim();

    final about = (profile['about'] ?? '').toString().trim();

    if (username.isEmpty ||
        !RegExp(r'^[a-z0-9_]{3,24}$').hasMatch(username)) {
      throw Exception(
        'Username должен содержать 3–24 символа: '
        'английские буквы, цифры или _',
      );
    }

    final userRef = _db.collection('users').doc(user.uid);
    final publicRef = _db.collection('public_users').doc(user.uid);
    final usernameRef = _db.collection('usernames').doc(username);

    await _db.runTransaction((transaction) async {
      final usernameSnapshot = await transaction.get(usernameRef);
      final userSnapshot = await transaction.get(userRef);

      final oldUsername =
          (userSnapshot.data()?['username'] ?? '')
              .toString()
              .toLowerCase();

      if (usernameSnapshot.exists &&
          usernameSnapshot.data()?['uid'] != user.uid) {
        throw Exception('Этот username уже занят');
      }

      if (oldUsername.isNotEmpty && oldUsername != username) {
        final oldRef = _db.collection('usernames').doc(oldUsername);
        final oldSnapshot = await transaction.get(oldRef);

        if (oldSnapshot.exists &&
            oldSnapshot.data()?['uid'] == user.uid) {
          transaction.delete(oldRef);
        }
      }

      transaction.set(usernameRef, {
        'uid': user.uid,
        'createdAt': FieldValue.serverTimestamp(),
      });

      transaction.set(userRef, {
        'uid': user.uid,
        'username': username,
        'usernameLower': username,
        'displayName': displayName,
        'about': about,
        'updatedAt': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));

      transaction.set(publicRef, {
        'uid': user.uid,
        'username': username,
        'usernameLower': username,
        'displayName': displayName,
        'avatarUrl': user.photoURL ?? '',
        'updatedAt': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
    });

    return {'success': true};
  }

  // ==========================================
  // USER SEARCH
  // ==========================================

  Future<Map<String, dynamic>> _searchUsers(
    Map<String, dynamic> args,
  ) async {
    final user = _user;

    final query = (args['query'] ?? '')
        .toString()
        .trim()
        .replaceFirst(RegExp(r'^@'), '')
        .toLowerCase();

    if (query.isEmpty) {
      return {'success': true, 'users': []};
    }

    final snapshot = await _db
        .collection('public_users')
        .orderBy('usernameLower')
        .startAt([query])
        .endAt(['$query\uf8ff'])
        .limit(20)
        .get();

    final users = snapshot.docs
        .where((doc) => doc.id != user.uid)
        .map(_document)
        .toList();

    return {
      'success': true,
      'users': users,
    };
  }

  // ==========================================
  // PRIVATE CHATS
  // ==========================================

  Future<Map<String, dynamic>> _createChat(
    Map<String, dynamic> args,
  ) async {
    final user = _user;

    final otherUid = (args['otherUid'] ?? '').toString().trim();

    if (otherUid.isEmpty || otherUid == user.uid) {
      throw Exception('Некорректный пользователь');
    }

    final members = [user.uid, otherUid]..sort();
    final chatId = members.join('_');

    final ref = _db.collection('chats').doc(chatId);
    final snapshot = await ref.get();

    if (!snapshot.exists) {
      await ref.set({
        'members': members,
        'type': 'private',
        'createdAt': FieldValue.serverTimestamp(),
        'updatedAt': FieldValue.serverTimestamp(),
        'lastMessage': '',
        'lastMessageAt': FieldValue.serverTimestamp(),
      });
    }

    return {
      'success': true,
      'chatId': chatId,
    };
  }

  Future<Map<String, dynamic>> _getChats() async {
    final user = _user;

    final snapshot = await _db
        .collection('chats')
        .where('members', arrayContains: user.uid)
        .orderBy('updatedAt', descending: true)
        .limit(50)
        .get();

    return {
      'success': true,
      'chats': snapshot.docs.map(_document).toList(),
    };
  }

  Future<Map<String, dynamic>> _sendMessage(
    Map<String, dynamic> args,
  ) async {
    final user = _user;

    final chatId = (args['chatId'] ?? '').toString();
    final message = (args['text'] ?? '').toString().trim();

    if (chatId.isEmpty || message.isEmpty) {
      throw Exception('Чат или сообщение пустые');
    }

    if (message.length > 10000) {
      throw Exception('Сообщение слишком длинное');
    }

    final chatRef = _db.collection('chats').doc(chatId);
    final chatSnapshot = await chatRef.get();

    if (!chatSnapshot.exists) {
      throw Exception('Чат не найден');
    }

    final members =
        List<String>.from(chatSnapshot.data()?['members'] ?? []);

    if (!members.contains(user.uid)) {
      throw Exception('Нет доступа к этому чату');
    }

    final messageRef = chatRef.collection('messages').doc();

    await _db.runTransaction((transaction) async {
      transaction.set(messageRef, {
        'senderId': user.uid,
        'text': message,
        'type': 'text',
        'createdAt': FieldValue.serverTimestamp(),
      });

      transaction.update(chatRef, {
        'lastMessage': message,
        'lastMessageSender': user.uid,
        'lastMessageAt': FieldValue.serverTimestamp(),
        'updatedAt': FieldValue.serverTimestamp(),
      });
    });

    return {
      'success': true,
      'messageId': messageRef.id,
    };
  }

  Future<Map<String, dynamic>> _getMessages(
    Map<String, dynamic> args,
  ) async {
    final user = _user;

    final chatId = (args['chatId'] ?? '').toString();

    if (chatId.isEmpty) {
      throw Exception('Не указан чат');
    }

    final chatRef = _db.collection('chats').doc(chatId);
    final chatSnapshot = await chatRef.get();

    if (!chatSnapshot.exists) {
      throw Exception('Чат не найден');
    }

    final members =
        List<String>.from(chatSnapshot.data()?['members'] ?? []);

    if (!members.contains(user.uid)) {
      throw Exception('Нет доступа к этому чату');
    }

    final snapshot = await chatRef
        .collection('messages')
        .orderBy('createdAt')
        .limit(100)
        .get();

    return {
      'success': true,
      'messages': snapshot.docs.map(_document).toList(),
    };
  }

  // ==========================================
  // GROUPS
  // ==========================================

  Future<Map<String, dynamic>> _createGroup(
    Map<String, dynamic> args,
  ) async {
    final user = _user;

    final name = (args['name'] ?? '').toString().trim();
    final description =
        (args['description'] ?? '').toString().trim();

    if (name.isEmpty) {
      throw Exception('Укажи название группы');
    }

    final memberUids = <String>{user.uid};

    final suppliedMembers = args['memberUids'];

    if (suppliedMembers is List) {
      for (final id in suppliedMembers) {
        final value = id.toString().trim();
        if (value.isNotEmpty) {
          memberUids.add(value);
        }
      }
    }

    final ref = _db.collection('groups').doc();

    await ref.set({
      'name': name,
      'description': description,
      'ownerUid': user.uid,
      'members': memberUids.toList(),
      'createdAt': FieldValue.serverTimestamp(),
      'updatedAt': FieldValue.serverTimestamp(),
    });

    return {
      'success': true,
      'groupId': ref.id,
    };
  }

  Future<Map<String, dynamic>> _getGroups() async {
    final user = _user;

    final snapshot = await _db
        .collection('groups')
        .where('members', arrayContains: user.uid)
        .limit(50)
        .get();

    return {
      'success': true,
      'groups': snapshot.docs.map(_document).toList(),
    };
  }

  // ==========================================
  // CHANNELS
  // ==========================================

  Future<Map<String, dynamic>> _createChannel(
    Map<String, dynamic> args,
  ) async {
    final user = _user;

    final name = (args['name'] ?? '').toString().trim();
    final username = (args['username'] ?? '')
        .toString()
        .trim()
        .replaceFirst(RegExp(r'^@'), '')
        .toLowerCase();

    final description =
        (args['description'] ?? '').toString().trim();

    final visibility =
        (args['visibility'] ?? 'Публичный').toString();

    if (name.isEmpty) {
      throw Exception('Укажи название канала');
    }

    if (visibility == 'Публичный' &&
        !RegExp(r'^[a-z0-9_]{3,24}$').hasMatch(username)) {
      throw Exception('Некорректный username канала');
    }

    final ref = _db.collection('channels').doc();

    await _db.runTransaction((transaction) async {
      DocumentReference<Map<String, dynamic>>? usernameRef;

      if (username.isNotEmpty) {
        usernameRef =
            _db.collection('channel_usernames').doc(username);

        final usernameSnapshot =
            await transaction.get(usernameRef);

        if (usernameSnapshot.exists) {
          throw Exception('Username канала уже занят');
        }

        transaction.set(usernameRef, {
          'channelId': ref.id,
          'ownerUid': user.uid,
          'createdAt': FieldValue.serverTimestamp(),
        });
      }

      transaction.set(ref, {
        'name': name,
        'username': username,
        'usernameLower': username,
        'description': description,
        'visibility': visibility,
        'ownerUid': user.uid,
        'members': [user.uid],
        'subscribers': 1,
        'createdAt': FieldValue.serverTimestamp(),
        'updatedAt': FieldValue.serverTimestamp(),
      });
    });

    return {
      'success': true,
      'channelId': ref.id,
    };
  }

  Future<Map<String, dynamic>> _getChannels() async {
    final user = _user;

    final snapshot = await _db
        .collection('channels')
        .where('ownerUid', isEqualTo: user.uid)
        .limit(50)
        .get();

    return {
      'success': true,
      'channels': snapshot.docs.map(_document).toList(),
    };
  }

  Future<Map<String, dynamic>> _createChannelPost(
    Map<String, dynamic> args,
  ) async {
    final user = _user;

    final channelId = (args['channelId'] ?? '').toString();
    final message = (args['text'] ?? '').toString().trim();

    if (channelId.isEmpty || message.isEmpty) {
      throw Exception('Канал или публикация пустые');
    }

    final channelRef = _db.collection('channels').doc(channelId);
    final channelSnapshot = await channelRef.get();

    if (!channelSnapshot.exists ||
        channelSnapshot.data()?['ownerUid'] != user.uid) {
      throw Exception('Нет доступа к каналу');
    }

    final postRef = channelRef.collection('posts').doc();

    await postRef.set({
      'text': message,
      'authorUid': user.uid,
      'createdAt': FieldValue.serverTimestamp(),
    });

    await channelRef.update({
      'updatedAt': FieldValue.serverTimestamp(),
    });

    return {
      'success': true,
      'postId': postRef.id,
    };
  }

  Future<Map<String, dynamic>> _getChannelPosts(
    Map<String, dynamic> args,
  ) async {
    final user = _user;

    final channelId = (args['channelId'] ?? '').toString();

    if (channelId.isEmpty) {
      throw Exception('Не указан канал');
    }

    final channelRef = _db.collection('channels').doc(channelId);
    final channelSnapshot = await channelRef.get();

    if (!channelSnapshot.exists) {
      throw Exception('Канал не найден');
    }

    final channel = channelSnapshot.data()!;

    final members = List<String>.from(channel['members'] ?? []);

    if (channel['visibility'] != 'Публичный' &&
        !members.contains(user.uid)) {
      throw Exception('Нет доступа к каналу');
    }

    final snapshot = await channelRef
        .collection('posts')
        .orderBy('createdAt', descending: true)
        .limit(50)
        .get();

    return {
      'success': true,
      'posts': snapshot.docs.map(_document).toList(),
    };
  }

  // ==========================================
  // SETTINGS
  // ==========================================

  Future<Map<String, dynamic>> _getSettings() async {
    final user = _user;

    final snapshot = await _db
        .collection('users')
        .doc(user.uid)
        .collection('private')
        .doc('settings')
        .get();

    return {
      'success': true,
      'settings': _clean(snapshot.data() ?? {}),
    };
  }

  Future<Map<String, dynamic>> _saveSettings(
    Map<String, dynamic> args,
  ) async {
    final user = _user;

    await _db
        .collection('users')
        .doc(user.uid)
        .collection('private')
        .doc('settings')
        .set({
      ...args,
      'updatedAt': FieldValue.serverTimestamp(),
    }, SetOptions(merge: true));

    return {'success': true};
  }

  // ==========================================
  // FOLDERS
  // ==========================================

  Future<Map<String, dynamic>> _getFolders() async {
    final user = _user;

    final snapshot = await _db
        .collection('users')
        .doc(user.uid)
        .collection('folders')
        .orderBy('createdAt')
        .get();

    return {
      'success': true,
      'folders': snapshot.docs.map(_document).toList(),
    };
  }

  Future<Map<String, dynamic>> _createFolder(
    Map<String, dynamic> args,
  ) async {
    final user = _user;

    final name = (args['name'] ?? '').toString().trim();

    if (name.isEmpty) {
      throw Exception('Укажи название папки');
    }

    final ref = _db
        .collection('users')
        .doc(user.uid)
        .collection('folders')
        .doc();

    await ref.set({
      'name': name,
      'createdAt': FieldValue.serverTimestamp(),
    });

    return {
      'success': true,
      'folderId': ref.id,
    };
  }

  // ==========================================
  // METHOD DISPATCHER
  // ==========================================

  Future<dynamic> _onInvokeMethod(
    String name,
    dynamic args,
  ) async {
    try {
      await _ensureInitialized();

      final data = _args(args);

      switch (name) {
        case 'get_auth_state':
          final currentUser =
              fb.FirebaseAuth.instance.currentUser;

          if (currentUser == null) {
            return {
              'success': true,
              'authenticated': false,
            };
          }

          await _ensureUserDocument(currentUser);
          return _userData(currentUser);

        case 'sign_in':
          final googleUser =
              await GoogleSignIn.instance.authenticate();

          final googleAuth = googleUser.authentication;
          final idToken = googleAuth.idToken;

          if (idToken == null) {
            throw Exception('Google ID token is missing');
          }

          final credential =
              fb.GoogleAuthProvider.credential(
            idToken: idToken,
          );

          final result = await fb.FirebaseAuth.instance
              .signInWithCredential(credential);

          final user = result.user;

          if (user == null) {
            throw Exception('Firebase user not found');
          }

          await _ensureUserDocument(user);
          return _userData(user);

        case 'sign_out':
          await fb.FirebaseAuth.instance.signOut();
          await GoogleSignIn.instance.signOut();
          return {'success': true};

        case 'get_user_profile':
          return await _getUserProfile();

        case 'save_user_profile':
          return await _saveUserProfile(data);

        case 'search_users':
          return await _searchUsers(data);

        case 'create_chat':
          return await _createChat(data);

        case 'get_chats':
          return await _getChats();

        case 'send_message':
          return await _sendMessage(data);

        case 'get_messages':
          return await _getMessages(data);

        case 'create_group':
          return await _createGroup(data);

        case 'get_groups':
          return await _getGroups();

        case 'create_channel':
          return await _createChannel(data);

        case 'get_channels':
          return await _getChannels();

        case 'create_channel_post':
          return await _createChannelPost(data);

        case 'get_channel_posts':
          return await _getChannelPosts(data);

        case 'get_settings':
          return await _getSettings();

        case 'save_settings':
          return await _saveSettings(data);

        case 'get_folders':
          return await _getFolders();

        case 'create_folder':
          return await _createFolder(data);

        default:
          return {
            'success': false,
            'error': 'Unknown method: $name',
          };
      }
    } catch (e, stack) {
      debugPrint('VibeGram Firebase error: $e');
      debugPrint('$stack');

      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  @override
  void update() {}

  @override
  void dispose() {
    control.removeInvokeMethodListener(_onInvokeMethod);
    super.dispose();
  }
}
