$(document).ready(function() {
	var original_word = $('.hide-word');
	var open_word = $('.open-word');
	original_word.hide();

	$(open_word).on('click', () => {
		original_word.show();
		open_word.hide();
	});

	function send_vote(vote, card_id, before_send, success, error) {
		$.ajax({
			type: 'POST',
			url: '/vote',
			data: {vote, card_id},
			beforeSend: before_send,
			success: success,
			error: error
		});
	}

	$('button.vote').click((e) => {
	window.testff = e;
	var button = e.target;
	var card_id = parseInt(button.dataset.cardId)
	var vote = parseInt(window.testff.target.dataset.cardVote);
	if (vote === 1) {
		vote = true;
	}
	else {
		vote = false;
	}
	button.disabled = true;

	send_vote(vote, card_id, 
		(before_send) => {
			button.disabled = true;
		},
		(response) => {
			button.disabled = false;
			$('span#positive').text(response.result.positive);
			$('span#negative').text(response.result.negative);
		}, 
		(error) => {
			button.disabled = false;
			alert('Error!')
		})

	});
});