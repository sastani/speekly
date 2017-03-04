import * as UIRouter from 'angular-ui-router';

function homeConfig($stateProvider: UIRouter.IStateProvider) : void {
	$stateProvider.state({
		name: 'home',
		url: '/',
		component: 'homeComponent'
	});
}

homeConfig.$inject = [
	'$stateProvider'
];

export default homeConfig;
