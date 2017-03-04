import * as ng from 'angular';

import HomeController from './home.controller.ts';

class homeComponent implements ng.IComponentOptions {
	public bindings : { [index : string] : string};
	public controller : ng.IComponentController;
	public templateUrl : string;

	constructor(){
		this.bindings = {};
		this.controller = HomeController;
		this.templateUrl = require('./home.component.tpl.html');
	}
}

export default homeComponent;