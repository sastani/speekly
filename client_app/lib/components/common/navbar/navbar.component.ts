import * as angular from 'angular';

import NavbarCtrl from './navbar.controller.ts';

class NavbarComponent implements angular.IComponentOptions {
	public bindings : { [index : string] : string};
	public controller : ng.IComponentController;
	public templateUrl : string;

	constructor(){
		this.bindings = {navbarItems: '<', label: '<'};
		this.controller = NavbarCtrl;
		this.templateUrl = require('./navbar.component.tpl.html');
	}
}

export default NavbarComponent;