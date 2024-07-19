/** @odoo-module **/
import { startWebClient } from '@web/start';
import { TecharingWebClient } from './tec_sharing';
import { prepareFavoriteMenuRegister } from './components/favorite_menu_registry';

prepareFavoriteMenuRegister();
startWebClient(TecharingWebClient);
