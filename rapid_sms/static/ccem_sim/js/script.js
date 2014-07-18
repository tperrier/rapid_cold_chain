function showHideMessagePanel(id){
	e = document.getElementById(id);
	if(e.style.display=='none')
		e.style.display='table-row';
	else if(e.style.display=='table-row')
		e.style.display='none';
}