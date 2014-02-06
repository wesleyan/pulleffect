
var board = ["", "", "", "", "", "", "", "", ""];

var turn = 0;

function buttonClick(clicked_id) {

    p1success = ["success", "Congratulations player 1!"];
    p2success = ["success", "Congratulations player 2!"];
    position = parseInt(clicked_id);

    if (turn == 0) {
        if (board[(position)] == "") {
            board[(position)] = 1;
            $('#' + clicked_id).text('X');
            if (board[0] == 1 && board[1] == 1 && board[2] == 1) {

                return displayAlerts([p1success]);
            } else if (board[3] == 1 && board[4] == 1 && board[5] == 1) {

                return displayAlerts([p1success]);
            } else if (board[6] == 1 && board[7] == 1 && board[8] == 1) {
                return displayAlerts([p1success]);
            } else if (board[0] == 1 && board[3] == 1 && board[6] == 1) {
                return displayAlerts([p1success]);
            } else if (board[1] == 1 && board[4] == 1 && board[7] == 1) {
                return displayAlerts([p1success]);
            } else if (board[2] == 1 && board[5] == 1 && board[8] == 1) {
                return displayAlerts([p1success]);
            } else if (board[0] == 1 && board[4] == 1 && board[8] == 1) {
                return displayAlerts([p1success]);
            } else if (board[2] == 1 && board[4] == 1 && board[6] == 1) {
                return displayAlerts([p1success]);
            }

            turn = 1;
            clicked_id = 0;
            position = 0;

        }
    } else if (turn == 1) {
        if (board[(position)] == "") {
            board[(position)] = 2;
            $('#' + clicked_id).text('O');

            if (board[0] == 2 && board[1] == 2 && board[2] == 2) {
                return displayAlerts([p2success]);
            } else if (board[3] == 2 && board[4] == 2 && board[5] == 2) {
                return displayAlerts([p2success]);
            } else if (board[6] == 2 && board[7] == 2 && board[8] == 2) {
                return displayAlerts([p2success]);
            } else if (board[0] == 2 && board[3] == 2 && board[6] == 2) {
                return displayAlerts([p2success]);
            } else if (board[1] == 2 && board[4] == 2 && board[7] == 2) {
                return displayAlerts([p2success]);
            } else if (board[2] == 2 && board[5] == 2 && board[8] == 2) {
                return displayAlerts([p2success]);
            } else if (board[0] == 2 && board[4] == 2 && board[8] == 2) {
                return displayAlerts([p2success]);
            } else if (board[2] == 2 && board[4] == 2 && board[6] == 2) {
                return displayAlerts([p2success]);
            }

            turn = 0;
            clicked_id = 0;
            position = 0;
        }
    }
}

function resetClick(reset_clicked) {
    for (var i = 0; i < board.length; i++) {
        if (board[i] != "") {
            board[i] = "";
        }

        for (var j = 0; j < board.length; j++) {
            $('#' + j).text('');
        }

        turn = 0;
        position = 0;
        clicked_id = 0;
    }
}


var loadTicTacToe = function() {
    var panel = $("<div />").width("300px");
    panel.addClass("panel panel-default")
    var table = $("<table />").addClass("table table-striped table-condensed");

    htmlStr = '\
    <div class="panel panel-default col-md-3" style="width=300;" id="tictac">\
		<div class="tictactoe" style="height:270px;">\
		    <div class="row">\
		        <button id="0" class="tic col-md-4" onClick="buttonClick(this.id)"/>\
		        <button id="1" class="tic col-md-4" onClick="buttonClick(this.id)"/>\
		        <button id="2" class="tic col-md-4" onClick="buttonClick(this.id)"/>\
		    </div>\
		    <div class="row">\
		        <button id="3" class="tic col-md-4" onClick="buttonClick(this.id)"/>\
		        <button id="4" class="tic col-md-4" onClick="buttonClick(this.id)"/>\
		        <button id="5" class="tic col-md-4" onClick="buttonClick(this.id)"/>\
		    </div>\
		    <div class="row">\
		        <button id="6" class="tic col-md-4" onClick="buttonClick(this.id)"/>\
		        <button id="7" class="tic col-md-4" onClick="buttonClick(this.id)"/>\
		        <button id="8" class="tic col-md-4" onClick="buttonClick(this.id)"/>\
		    </div>\
		    <div class="row">\
		        <button id="9" class="reset col-md-4" onClick="resetClick(true)">Reset</button>\
		    </div>\
		</div>\
	</div>';
    panel.append(table);
	$('.content').append(htmlStr);
}