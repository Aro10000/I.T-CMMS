/** @odoo-module */

import { KanbanModel } from "@web/views/kanban/kanban_model";

import { TecTaskKanbanDynamicGroupList } from "./tec_task_kanban_dynamic_group_list";
import { TecTaskRecord } from './tec_task_kanban_record';

export class TecTaskKanbanGroup extends KanbanModel.Group {
    get isPersonalStageGroup() {
        return !!this.groupByField && this.groupByField.name === 'personal_stage_type_ids';
    }

    async delete() {
        if (this.isPersonalStageGroup) {
            this.deleted = true;
            return await this.model.orm.call(this.resModel, 'remove_personal_stage', [this.resId]);
        } else {
            return await super.delete();
        }
    }
}

export class TecTaskKanbanModel extends KanbanModel { }

TecTaskKanbanModel.DynamicGroupList = TecTaskKanbanDynamicGroupList;
TecTaskKanbanModel.Group = TecTaskKanbanGroup;
TecTaskKanbanModel.Record = TecTaskRecord;
