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
	})
});