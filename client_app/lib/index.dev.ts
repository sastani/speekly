//main dependencies
import * as angular from 'angular';
import 'angular-ui-router';
import 'angular-resource/angular-resource.js';
import 'angular-mocks';

//database service
import 'ng-simpledb';

//styles
import './styles/bootstrap/_bootstrap.scss';
import './styles/style.css';

//components
import Components from './components/index.ts';

//services
import Services from './services/index.ts';

angular.module('client_app', [
	'ui.router',
	'ngResource',
	'ngMockE2E',
	'ngSimpleDb',
	Components,
	Services
]);
