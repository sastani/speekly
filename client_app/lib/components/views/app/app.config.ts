import * as angular from 'angular';

function appConfig($locationProvider : angular.ILocationProvider)
{
	$locationProvider.html5Mode(true);
}

appConfig.$inject = [
	'$locationProvider'
];

export default appConfig;