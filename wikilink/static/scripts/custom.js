$(document).ready(function(){
 $("#jqtest").html("DEBUG: JQuery is working.");
	
$('h2.sectionheader').find('ul').hide().end().click(function() {
     $(this).next().slideToggle();
   });

});

	
	