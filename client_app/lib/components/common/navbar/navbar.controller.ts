import * as ng from 'angular';

import { navbarItem } from '../../../utils/interfaces.ts';


class navbarCtrl implements ng.IComponentController{
	public navbarItems : Array<navbarItem>;
	constructor(){}
}

export default navbarCtrl;