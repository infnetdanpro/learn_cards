var original_word = $('.hide-word');
var open_word = $('.open-word');
original_word.hide();

$(open_word).on('click', () => {
	original_word.show();
	open_word.hide();
});