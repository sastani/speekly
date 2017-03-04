import * as ng from 'angular';

import navbarItems from './app.navbar.ts';

class AppController implements ng.IComponentController{
	public navbarItems : any;
	public label : string;

	constructor(private $http : ng.IHttpService){
		this.navbarItems = navbarItems;
		this.label = 'Widget Factory';
	}
}

AppController.$inject = [];

export default AppController;