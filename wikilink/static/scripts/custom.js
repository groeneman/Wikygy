$(document).ready(function(){
 $("#jqtest").html("DEBUG: JQuery is working.");
	
$('.source').find('ul').hide().end().find('p').click(function() {
     $(this).next().slideToggle();
   });

});

	
	