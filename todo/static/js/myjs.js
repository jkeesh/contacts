$(document).ready(function(){
	$(".datepicker").datepicker().on('changeDate', function(ev){
		var newDate = $(this).val();
		console.log(newDate);

		$.ajax({
			url: '/change_date',
			data: {
				date: newDate,
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


	$(".filter-buttons .btn").click(function(){
		$this = $(this);
		console.log($this);

		var filter = $this.attr('data-filter');
		window.location.href = '/filter?filter='+filter;
	});

//
//   var converter = new Markdown.Converter();
//   var html = converter.makeHtml(text);
//
//   alert(html);

	var converter = new Markdown.Converter();


	$(".note .text").each(function(idx, elem){
		$this = $(this);
		var old = $this.html();
		var html = converter.makeHtml(old);
		$this.html(html);
	});
});