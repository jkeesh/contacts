$(document).ready(function(){

	// Save the new date for the contact when you change the date with datepicker.
	$(".datepicker").datepicker().on('changeDate', function(ev){

		function getDateString(date){
			var month = date.getMonth() + 1;
			var dayOfMonth = date.getDate();
			var year = date.getFullYear() - 2000;
			return month + '/' + dayOfMonth + '/' + year;
		}

		$.ajax({
			url: '/change_date',
			data: {
				date: getDateString(ev.date),
				c_id: $(this).attr('data-contact-id')
			},
			type: 'POST',
			dataType: 'JSON',
			success: function(resp){
				console.log(resp);
				window.location.reload();
			}
		});


	});


	// When you click a button go to the proper filter page
	$(".filter-buttons .btn").click(function(){
		$this = $(this);
		var filter = $this.attr('data-filter');
		window.location.href = '/filter?filter='+filter;
	});


	// When you click the done button mark the users date as done
	$('.done-button').click(function(){
		$this = $(this);
		$.ajax({
			url: '/contact_done',
			data: {
				c_id: $this.attr('data-contact-id')
			},
			type: 'POST',
			dataType: 'JSON',
			success: function(resp){
				console.log(resp);
				window.location.reload();
			}
		});
	});



	// Make all notes use Markdown
	var converter = new Markdown.Converter();

	$(".note .text").each(function(idx, elem){
		$this = $(this);
		var old = $this.html();
		var html = converter.makeHtml(old);
		$this.html(html);
	});
});