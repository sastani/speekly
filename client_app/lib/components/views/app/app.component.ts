import * as ng from 'angular';

import AppController from './app.controller.ts';

class appComponent implements ng.IComponentOptions {
	public bindings : { [index : string] : string};
	public controller : ng.IComponentController;
	public templateUrl : string;

	constructor(){
		this.bindings = {};
		this.controller = AppController;
		this.templateUrl = require('./app.component.tpl.html');
	}
}

export default appComponent;