/*
 * This is the js that makes the django_private_chat/dialogs.html page work
 * The variables base_ws_server_path and session_key and the function 
 * getOpponentUsername need to be set before this file is loaded in order 
 * for this to work
 */
$(document).ready(function () {
    var websocket = null;


    // TODO: Use for adding new dialog
    function addNewUser(packet) {
        $('#user-list').html('');
        packet.value.forEach(function (userInfo) {
            if (userInfo.username == getUsername()) return;
            var tmpl = Handlebars.compile($('#user-list-item-template').html());
            $('#user-list').append(tmpl(userInfo))
        });
    }

    function addNewMessage(packet) {
        var msg_class = "";
        if (packet['sender_name'] == $("#owner_username").val()) {
            msg_class = "pull-left";
        } else {
            msg_class = "pull-right";
        }
        var msgElem =
            $('<div class="row">' +
                '<p class="' + msg_class + '">' +
                '<span class="username">' + packet['sender_name'] + ': </span>' +
                packet['message'] +
                ' <span class="timestamp">&ndash; <span data-livestamp="' + packet['created'] + '"> ' + packet['created'] + '</span></span> ' +
                '</p> ' +
                '</div>');
        $('#messages').append(msgElem);
        scrollToLastMessage()
    }

    function scrollToLastMessage() {
        var $msgs = $('#messages');
        $msgs.animate({"scrollTop": $msgs.prop('scrollHeight')})
    }

    function generateMessage(context) {
        var tmpl = Handlebars.compile($('#chat-message-template').html());
        return tmpl({msg: context})
    }

    function setUserOnlineOffline(username, online) {
        var elem = $("#user-" + username);
        if (online) {
            elem.attr("class", "btn btn-success");
        } else {
            elem.attr("class", "btn btn-danger");
        }
    }

    function gone_online() {
        $("#offline-status").hide();
        $("#online-status").show();
    }

    function gone_offline() {
        $("#online-status").hide();
        $("#offline-status").show();
    }
    function flash_user_button(username){
        var btn = $("#user-"+username);
        btn.fadeTo(700, 0.1, function() { $(this).fadeTo(800, 1.0); });
    }
    function setupChatWebSocket() {
        var opponent_username = getOpponnentUsername();
        websocket = new WebSocket(base_ws_server_path + session_key + '/' + opponent_username);

        websocket.onopen = function (event) {
            var opponent_username = getOpponnentUsername();

            var onOnlineCheckPacket = JSON.stringify({
                type: "check-online",
                session_key: session_key,
                username: opponent_username
                // Sending username because the user needs to know if his opponent is online
            });
            var onConnectPacket = JSON.stringify({
                type: "online",
                session_key: session_key

            });

            console.log('connected, sending:', onConnectPacket);
            websocket.send(onConnectPacket);
            console.log('checking online opponents with:', onOnlineCheckPacket);
            websocket.send(onOnlineCheckPacket);
        };


        window.onbeforeunload = function () {

            var onClosePacket = JSON.stringify({
                type: "offline",
                session_key: session_key,
                username: opponent_username,
                // Sending username because to let opponnent know that the user went offline
            });
            console.log('unloading, sending:', onClosePacket);
            websocket.send(onClosePacket);
            websocket.close();
        };


        websocket.onmessage = function (event) {
            var packet;

            try {
                packet = JSON.parse(event.data);
                console.log(packet)
            } catch (e) {
                console.log(e);
            }

            switch (packet.type) {
                case "new-dialog":
                    // TODO: add new dialog to dialog_list
                    break;
                case "user-not-found":
                    // TODO: dispay some kind of an error that the user is not found
                    break;
                case "gone-online":
                    if (packet.usernames.indexOf(opponent_username) != -1) {
                        gone_online();
                    } else {
                        gone_offline();
                    }
                    for (var i = 0; i < packet.usernames.length; ++i) {
                        setUserOnlineOffline(packet.usernames[i], true);
                    }
                    break;
                case "gone-offline":
                    if (packet.username == opponent_username) {
                        gone_offline();
                    }
                    setUserOnlineOffline(packet.username, false);
                    break;
                case "new-message":
                    if (packet['sender_name'] == opponent_username || packet['sender_name'] == $("#owner_username").val()){
                        addNewMessage(packet);
                    } else {
                        flash_user_button(packet['sender_name']);
                    }
                    break;
                case "opponent-typing":
                    var typing_elem = $('#typing-text');
                    if (!typing_elem.is(":visible")) {
                        typing_elem.fadeIn(500);
                    } else {
                        typing_elem.stop(true);
                        typing_elem.fadeIn(0);
                    }
                    typing_elem.fadeOut(3000);
                    break;

                default:
                    console.log('error: ', event)
            }
        }
    }

    function sendMessage(message) {
        var opponent_username = getOpponnentUsername();
        var newMessagePacket = JSON.stringify({
            type: 'new-message',
            session_key: session_key,
            username: opponent_username,
            message: message
        });
        websocket.send(newMessagePacket)
    }

    $('#chat-message').keypress(function (e) {
        if (e.which == 13 && this.value) {
            sendMessage(this.value);
            this.value = "";
            return false
        } else {
            var opponent_username = getOpponnentUsername();
            var packet = JSON.stringify({
                type: 'is-typing',
                session_key: session_key,
                username: opponent_username,
                typing: true
            });
            websocket.send(packet);
        }
    });

    $('#btn-send-message').click(function (e) {
        var $chatInput = $('#chat-message');
        var msg = $chatInput.val();
        if (!msg) return;
        sendMessage($chatInput.val());
        $chatInput.val('')
    });
    
    // sends a message when you click the videochat button
    $('#btn-video-call').click(function (e) { 
        sendMessage($('#vc-link-message-template').html());
    });

    setupChatWebSocket();
    scrollToLastMessage();
});