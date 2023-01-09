create table udo_job
(
    id            varchar(191) not null
        primary key,
    next_run_time double       null,
    job_state     blob         not null
);

create index ix_udo_job_next_run_time
    on udo_job (next_run_time);

create table udo_job_info
(
    id            bigint(255) auto_increment
        primary key,
    job_id        varchar(255)                       not null comment '任务编号',
    job_name      varchar(255)                       not null comment '任务名称',
    rule_code     varchar(2000)                      not null comment '规则编号',
    `trigger`     varchar(255)                       not null comment '执行器模式：interval定时执行;date一次执行;cron式定时调度',
    run_date      datetime                           null comment '任务执行时间',
    start_date    datetime                           null comment '任务开始时间',
    end_date      datetime                           null comment '任务结束时间',
    year          varchar(255)                       null,
    month         varchar(255)                       null,
    week          varchar(255)                       null,
    day           varchar(255)                       null,
    day_of_week   varchar(255)                       null comment '一周第几天',
    hour          varchar(255)                       null,
    minute        varchar(255)                       null,
    second        varchar(255)                       null,
    next_run_time datetime                           null comment '下次执行时间',
    status        int(255)                           not null comment '任务状态 1 有效 2 无效',
    create_time   datetime default CURRENT_TIMESTAMP null comment '创建时间',
    update_time   datetime default CURRENT_TIMESTAMP null comment '修改时间',
    create_user   varchar(255)                       null comment '创建人',
    update_user   varchar(255)                       null comment '更新人',
    project_code  varchar(255)                       null comment '项目编号',
    is_run        int(2)   default 1                 null comment '任务是否运行状态:0 运行 1 停止'
);

create table udo_metadata
(
    id       bigint auto_increment comment 'id'
        primary key,
    type     varchar(50)              not null comment 'type',
    code     varchar(50)              not null comment 'code',
    parent   varchar(50) default '-1' not null comment 'parent',
    value    varchar(50)              not null comment 'value',
    sort     int         default 0    not null comment 'sort',
    multiple int(2)                   null comment 'multiple',
    constraint uniq_metadata
        unique (type, value, parent)
);

create table udo_operate_log
(
    id           bigint auto_increment comment 'id'
        primary key,
    url          varchar(255)                       not null comment 'url',
    type         varchar(50)                        null comment '操作类型：例如：add；update；delete',
    db_code      varchar(255)                       null comment 'db code',
    project_code varchar(255)                       null comment 'project code',
    rule_code    varchar(2000)                      null comment 'rule code',
    job_code     varchar(255)                       null comment 'job code',
    ip           varchar(255)                       null comment 'ip',
    request_body text                               null comment 'request body',
    output       varchar(255)                       null comment 'output',
    create_time  datetime default CURRENT_TIMESTAMP null comment '创建时间',
    create_user  varchar(255)                       null comment '创建人'
);

create table udo_project
(
    id                  bigint auto_increment comment 'id'
        primary key,
    project_code        varchar(50)                          not null comment '项目编码',
    project_name        varchar(50)                          not null comment '项目名称',
    project_description varchar(255)                         null comment '项目描述',
    create_time         datetime   default CURRENT_TIMESTAMP null comment '创建时间',
    create_user         varchar(255)                         null comment '创建人',
    update_time         datetime   default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    update_user         varchar(255)                         null comment '更新人',
    is_delete           varchar(2) default '0'               not null comment '0 已存在 1 已删除',
    we_work_robot       varchar(60)                          null comment '企业微信机器人id',
    constraint uniq_project_code
        unique (project_code),
    constraint uniq_project_name
        unique (project_name)
);

create table udo_project_user
(
    id           bigint auto_increment comment 'id'
        primary key,
    project_code varchar(50)                        not null comment 'project code',
    username     varchar(50)                        not null comment 'username',
    create_time  datetime default CURRENT_TIMESTAMP null comment '创建时间',
    create_user  varchar(255)                       null comment '创建人',
    update_time  datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    update_user  varchar(255)                       null comment '更新人',
    constraint project_code_username
        unique (project_code, username)
);

create table udo_rule
(
    id                    bigint auto_increment
        primary key,
    rule_code             varchar(50)                        not null comment '校验规则编号',
    rule_name             varchar(255)                       not null comment '校验规则名称',
    rule_description      varchar(512)                       null comment '规则描述',
    rule_type             varchar(50)                        not null comment '规则类型',
    check_source_type     varchar(50)                        null comment '需要校验的数据源类型',
    check_db_code         varchar(255)                       not null comment '需要校验的数据库编号',
    check_db_name         varchar(255)                       null comment '需要校验的数据库名称',
    check_table_code      varchar(4000)                      null comment '需要校验的表编号',
    check_table_name      varchar(4000)                      null comment '需要校验的表名称',
    contrast_source_type  varchar(255)                       null comment '对比的数据源类型',
    contrast_db_code      varchar(255)                       null comment '对比数据库编号',
    contrast_db_name      varchar(255)                       null comment '对比数据库名称',
    contrast_table_code   varchar(4000)                      null comment '对比表编号',
    contrast_table_name   varchar(4000)                      null comment '对比表名称',
    execution_cycle       varchar(255)                       null comment '执行周期',
    next_execution_time   varchar(255)                       null comment '下次执行时间',
    last_execution_time   varchar(255)                       null comment '上次执行时间',
    last_execution_status varchar(255)                       null comment '上次执行状态',
    create_time           datetime default CURRENT_TIMESTAMP null comment '创建时间',
    create_user           varchar(255)                       null comment '创建人',
    update_time           datetime default CURRENT_TIMESTAMP null comment '更新时间',
    update_user           varchar(255)                       null comment '更新人',
    check_table_sql       text                               null comment '需要校验的表sql',
    contrast_table_sql    text                               null comment '对比表sql',
    project_code          varchar(255)                       null comment '项目编号',
    alert_user            varchar(500)                       null comment '告警通知的用户'
);

create table udo_rule_info
(
    id               bigint(255) auto_increment
        primary key,
    rule_code        varchar(255)                         not null comment '规则编码',
    col              varchar(255)                         not null comment '字段名',
    operator         varchar(255)                         null comment '运算符',
    expected_value   varchar(255)                         null comment '预期值',
    operator_type    varchar(255)                         null comment '操作类型 1:select 2:where 3：维度字段',
    role_information varchar(255)                         null comment '角色身份（1：原始表，2：对比表）',
    create_time      datetime   default CURRENT_TIMESTAMP null comment '创建时间',
    update_time      datetime   default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    expression       tinyint(1) default 0                 null comment '是否表达式',
    aggregate_type   varchar(20)                          null comment 'sum;count'
);

create table udo_rule_log
(
    id               bigint(255) auto_increment
        primary key,
    rule_code        varchar(255)                        not null comment '规则编号',
    rule_name        varchar(255)                        not null comment '规则名称',
    rule_description varchar(512)                        null comment '规则描述',
    rule_type        varchar(255)                        not null comment '规则类型',
    start_time       timestamp default CURRENT_TIMESTAMP not null comment '开始时间',
    end_time         timestamp                           null comment '结束时间',
    status           int(1)                              null comment '状态 1：成功 2：失败 3：执行中',
    check_status     int(1)                              null comment '检查结果的状态 1：成功 2：失败',
    content          longtext                            null comment '执行日志',
    project_code     varchar(255)                        null comment '项目编号',
    project_name     varchar(255)                        null comment '项目名称'
);

create table udo_source_database
(
    id          int auto_increment
        primary key,
    source_type varchar(255)                       null comment '数据源类型',
    source_name varchar(255)                       null comment '数据源名称',
    host        varchar(255)                       null comment '数据库IP',
    db_code     varchar(255)                       null comment '数据库编码',
    db_name     varchar(255)                       null comment '数据库名称',
    port        varchar(255)                       null comment '数据库端口',
    user        varchar(255)                       null comment '用户名',
    password    varchar(255)                       null comment '密码',
    create_time datetime default CURRENT_TIMESTAMP null comment '创建时间',
    update_time datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint 唯一索引
        unique (source_type, host, db_name) comment '唯一索引'
);

create table udo_source_field
(
    id             int(255) auto_increment
        primary key,
    source_type    varchar(16)                        not null comment '数据源类型',
    db_code        varchar(255)                       not null comment '数据库编号',
    table_code     varchar(255)                       not null comment '表编号',
    field_name     varchar(255)                       not null comment '字段名称',
    field_type     varchar(128)                       null comment '字段类型',
    field_describe varchar(1000)                      null comment '字段描述',
    Index_info     varchar(255)                       null comment '索引信息',
    primary_key    varchar(255)                       null comment '主键信息',
    is_null        varchar(255)                       null comment '是否可为空',
    default_value  varchar(255)                       null comment '默认值',
    create_time    datetime default CURRENT_TIMESTAMP null comment '创建时间',
    update_time    datetime default CURRENT_TIMESTAMP null comment '更新时间'
);

create table udo_source_table
(
    id          int(255) auto_increment comment 'id'
        primary key,
    source_type varchar(16)                        not null comment '数据源类型',
    db_code     varchar(255)                       not null comment '数据库编号',
    table_code  varchar(255)                       not null comment '表编号',
    table_name  varchar(256)                       not null comment '表名',
    create_time datetime default CURRENT_TIMESTAMP null comment '创建时间',
    update_time datetime default CURRENT_TIMESTAMP null comment '更新时间',
    constraint 唯一索引
        unique (source_type, db_code, table_name)
);

create table udo_user
(
    id              bigint auto_increment comment 'id'
        primary key,
    first_name      varchar(255)                        not null comment 'firstName',
    last_name       varchar(255)                        not null comment 'lastName',
    username        varchar(255)                        not null comment 'username',
    email           varchar(255)                        not null comment 'email',
    phone           varchar(255)                        null comment 'phone',
    create_user     varchar(255)                        null comment 'create user',
    create_time     timestamp default CURRENT_TIMESTAMP not null comment 'create time',
    update_user     varchar(255)                        null comment 'update user',
    update_time     timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment 'update time',
    last_login_time timestamp default CURRENT_TIMESTAMP null,
    password        varchar(255)                        null comment 'password',
    constraint uniq_username
        unique (username)
);

insert into udo_user (first_name, last_name, username, email, password)
values ('admin', 'admin', 'admin', 'admin@admin.com', 'e10adc3949ba59abbe56e057f20f883e');

