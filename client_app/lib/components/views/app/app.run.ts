import * as ngDB from 'ng-simpledb';

function appRun(ngSimpleStore : ngDB.IDbServiceClass, $httpBackend : ng.IHttpBackendService){
	ngSimpleStore.setup($httpBackend);
}

appRun.$inject = [
	'ngSimpleStore',
	'$httpBackend'
];

export default appRun;