let observedElements = document.querySelectorAll('.fade-in'); // Define the elements you want to intiate an action on

const options = {
	threshold: 0.25
}

const inViewCallback = entries => {
	entries.forEach(entry => {
		if (entry.isIntersecting) {
			entry.target.classList.add('is-visible');
		}
	});
}

let observer = new IntersectionObserver(inViewCallback, options);

observedElements.forEach(element => {
	observer.observe(element);
});