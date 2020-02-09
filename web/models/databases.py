# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  Javen Yan
@File: databases.py
@Software: PyCharm
@Time :    2019/12/5 上午10:48
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, TEXT, ForeignKey, Boolean, Enum, DateTime, and_, or_, cast, DATE
from sqlalchemy.orm import relationship
from web.models.dbSession import ModelBase, dbSession as db, reconnect_db
import time
from logzero import logger

if db.is_active:
    dbSession = db
else:
    dbSession = reconnect_db()


def format_time(_time):
    """格式化时间"""
    return _time.strftime('%Y-%m-%d %H:%M:%S') if _time else ''


class SariRecord(ModelBase):
    __tablename__ = 'sari_records'

    id = Column(Integer, autoincrement=True, primary_key=True)
    country = Column(String(32), comment="国家")
    provinceName = Column(String(32), comment="省份")
    provinceShortName = Column(String(32), comment="省份缩写")
    cityName = Column(String(32), comment="城市")
    confirmedCount = Column(Integer, default=0, comment="确诊")
    suspectedCount = Column(Integer, default=0, comment="疑似")
    curedCount = Column(Integer, default=0, comment="治愈")
    deadCount = Column(Integer, default=0, comment="死亡")
    comment = Column(TEXT, nullable=True, comment="备注信息")
    updateTime = Column(Integer, nullable=True, comment="更新时间")

    @classmethod
    def by_id(cls, kid):
        return dbSession.query(cls).filter_by(id=kid).first()

    @classmethod
    def all(cls):
        return dbSession.query(cls).all()

    @classmethod
    def by_country(cls):
        return dbSession.query(cls).filter(SariRecord.country != '中国').all()

    @classmethod
    def update_and_insert(cls, **kwargs):
        province = kwargs.get('provinceName')
        city = kwargs.get('cityName')
        row = dbSession.query(cls) \
            .filter(and_(SariRecord.provinceName == province,
                         SariRecord.cityName == city)) \
            .first()
        if row:
            logger.debug("已经存在 更新数据")
            try:
                for k, v in kwargs.items():
                    setattr(row, k, v)
                dbSession.commit()
            except Exception as e:
                logger.error("Update Error " + str(e))
        else:
            logger.debug("不存在 新增数据")
            try:
                new_row = SariRecord(**kwargs)
                dbSession.add(new_row)
                dbSession.commit()
            except Exception as e:
                logger.error("Insert Error " + str(e))

    @classmethod
    def by_province(cls, province):
        return dbSession.query(cls) \
            .filter(SariRecord.provinceName.like('%{}%'.format(province))).all()

    @property
    def _update_at(self):
        if self.updateTime:
            tmp = time.localtime(self.updateTime)
            return time.strftime("%Y-%m-%d %H:%M:%S", tmp)

    def to_dict(self):
        return {
            "country": self.country,
            "provinceName": self.provinceName,
            "provinceShortName": self.provinceShortName,
            "cityName": self.cityName,
            "confirmedCount": self.confirmedCount,
            "suspectedCount": self.suspectedCount,
            "curedCount": self.curedCount,
            "deadCount": self.deadCount,
            "updateTime": self._update_at
        }


class SariOverall(ModelBase):
    __tablename__ = 'sari_overall'
    id = Column(Integer, autoincrement=True, primary_key=True)
    infectSource = Column(String(255), comment="传染源")
    passWay = Column(String(255), comment="传播途径")
    dailyPic = Column(String(255), comment="图片")
    summary = Column(TEXT, comment="汇总")
    countRemark = Column(String(255), comment="全国疫情信息概览")
    confirmedCount = Column(Integer, default=0, comment="确诊")
    seriousCount = Column(Integer, default=0, comment="确诊")
    confirmedIncr = Column(Integer, default=0, comment="新增")
    suspectedIncr = Column(Integer, default=0, comment="新增")
    seriousIncr = Column(Integer, default=0, comment="新增")
    curedIncr = Column(Integer, default=0, comment="治愈新增")
    deadIncr = Column(Integer, default=0, comment="死亡新增")
    suspectedCount = Column(Integer, default=0, comment="疑似感染人数")
    curedCount = Column(Integer, default=0, comment="治愈")
    deadCount = Column(Integer, default=0, comment="死亡")
    comment = Column(TEXT, nullable=True, comment="备注信息")
    virus = Column(String(255), nullable=True, comment="病毒")
    remark1 = Column(TEXT, nullable=True, comment="备注信息1")
    remark2 = Column(TEXT, nullable=True, comment="备注信息2")
    remark3 = Column(TEXT, nullable=True, comment="备注信息3")
    remark4 = Column(TEXT, nullable=True, comment="备注信息4")
    remark5 = Column(TEXT, nullable=True, comment="备注信息5")
    generalRemark = Column(TEXT, nullable=True, comment="备注信息")
    abroadRemark = Column(TEXT, nullable=True, comment="备注信息")
    updateTime = Column(Integer, nullable=True, comment="更新时间")

    @classmethod
    def by_id(cls, kid):
        return dbSession.query(cls).filter_by(id=kid).first()

    @classmethod
    def by_lasted(cls):
        return dbSession.query(cls).order_by(-cls.updateTime).first()

    @classmethod
    def by_limit(cls, num):
        return dbSession.query(cls).order_by(-cls.updateTime).limit(num)

    @property
    def _update_at(self):
        if self.updateTime:
            tmp = time.localtime(self.updateTime)
            return time.strftime("%Y-%m-%d %H:%M:%S", tmp)

    @staticmethod
    def keys():
        return ["infectSource",
                "passWay",
                "dailyPic",
                "summary",
                "countRemark",
                "confirmedCount",
                "suspectedCount",
                "curedCount",
                "deadCount",
                "virus",
                "remark1",
                "remark2",
                "remark3",
                "remark4",
                "remark5",
                "generalRemark",
                "confirmedIncr",
                "curedIncr",
                "deadIncr",
                "seriousIncr",
                "seriousCount",
                "suspectedIncr",
                "abroadRemark",
                "updateTime"]

    @classmethod
    def update_and_insert(cls, **kwargs):
        infectSource = kwargs.get('infectSource')
        updateTime = int(str(kwargs.get('updateTime'))[:-3]) if kwargs.get('updateTime') else None
        row = dbSession.query(cls) \
            .filter(and_(SariOverall.infectSource == infectSource,
                         SariRecord.updateTime == updateTime)) \
            .first()
        if row:
            logger.debug("头条 已经存在 更新数据")
            try:
                tmp = dict()
                for k in kwargs.keys():
                    if k in SariOverall.keys():
                        tmp.setdefault(k, kwargs.get(k))
                for k, v in tmp.items():
                    setattr(row, k, v)
                dbSession.commit()
            except Exception as e:
                logger.error("Update Error " + str(e))
        else:
            logger.debug("头条 不存在 新增数据")
            try:
                tmp = dict()
                for k in kwargs.keys():
                    if k in SariOverall.keys():
                        tmp.setdefault(k, kwargs.get(k))
                new_row = SariOverall(**tmp)
                dbSession.add(new_row)
                dbSession.commit()
            except Exception as e:
                logger.error("Insert Error " + str(e))

    def to_dict(self):
        return {
            "infectSource": self.infectSource,
            "passWay": self.passWay,
            "dailyPic": self.dailyPic,
            "summary": self.summary,
            "countRemark": self.countRemark,
            "confirmedCount": self.confirmedCount,
            "suspectedCount": self.suspectedCount,
            "curedCount": self.curedCount,
            "deadCount": self.deadCount,
            "virus": self.virus,
            "remark1": self.remark1,
            "remark2": self.remark2,
            "remark3": self.remark3,
            "remark4": self.remark4,
            "remark5": self.remark5,
            "generalRemark": self.generalRemark,
            "confirmedIncr": self.confirmedIncr,
            "curedIncr": self.curedIncr,
            "deadIncr": self.deadIncr,
            "seriousIncr": self.seriousIncr,
            "seriousCount": self.seriousCount,
            "suspectedIncr": self.suspectedIncr,
            "abroadRemark": self.abroadRemark,
            "updateTime": self._update_at
        }


class SariNews(ModelBase):
    __tablename__ = 'sari_news'
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String(128), comment="标题")
    summary = Column(TEXT, comment="概述")
    infoSource = Column(String(64), comment="来源")
    sourceUrl = Column(String(255), comment="来源地址")
    provinceId = Column(String(24), comment="省份地址")
    provinceName = Column(String(128), comment="省份")
    pubDate = Column(Integer, nullable=True, comment="发布时间")

    @classmethod
    def by_id(cls, kid):
        return dbSession.query(cls).filter_by(id=kid).first()

    @classmethod
    def by_lasted(cls):
        return dbSession.query(cls).order_by(-cls.pubDate).first()

    @classmethod
    def all(cls):
        return dbSession.query(cls).all()

    @classmethod
    def paginate(cls, page=1, page_size=10, location=None):
        start = page_size * (page - 1)
        end = page * page_size
        if location:
            return dbSession.query(cls).filter(SariNews.provinceName.like('%{}%'.format(location))).order_by(
                -cls.pubDate).slice(start, end).all()
        else:
            return dbSession.query(cls).order_by(-cls.pubDate).slice(start, end).all()

    @property
    def _pub_date(self):
        if self.pubDate:
            tmp = time.localtime(self.pubDate)
            return time.strftime("%Y-%m-%d %H:%M:%S", tmp)

    @classmethod
    def update_and_insert(cls, **kwargs):
        title = kwargs.get('title')
        row = dbSession.query(cls).filter(SariNews.title == title).first()
        if row:
            logger.debug("新闻 已经存在 更新数据")
            try:
                for k, v in kwargs.items():
                    setattr(row, k, v)
                dbSession.commit()
            except Exception as e:
                logger.error("Update Error " + str(e))
        else:
            logger.debug("新闻 不存在 新增数据")
            try:
                new_row = SariNews(**kwargs)
                dbSession.add(new_row)
                dbSession.commit()
            except Exception as e:
                logger.error("Insert Error " + str(e))

    def to_dict(self):
        return {
            "pubDate": self._pub_date,
            "title": self.title,
            "summary": self.summary,
            "infoSource": self.infoSource,
            "sourceUrl": self.sourceUrl,
            "provinceId": self.provinceId,
            "provinceName": self.provinceName
        }


class SariRumors(ModelBase):
    __tablename__ = 'sari_rumors'
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String(128), comment="标题")
    body = Column(TEXT, comment="辟谣内容全文")
    mainSummary = Column(TEXT, comment="辟谣内容概述")
    sourceUrl = Column(String(255), comment="来源地址")

    @classmethod
    def by_id(cls, kid):
        return dbSession.query(cls).filter_by(id=kid).first()

    @classmethod
    def all(cls):
        return dbSession.query(cls).all()

    @classmethod
    def by_limit(cls, num):
        return dbSession.query(cls).limit(num)

    @classmethod
    def paginate(cls, page=1, page_size=10):
        start = page_size * (page - 1)
        end = page * page_size
        return dbSession.query(cls).slice(start, end).all()

    @classmethod
    def update_and_insert(cls, **kwargs):
        title = kwargs.get('title')
        row = dbSession.query(cls).filter(SariRumors.title == title).first()
        if row:
            logger.debug("SariRumors 已经存在 更新数据")
            try:
                for k, v in kwargs.items():
                    if k == 'id':
                        continue
                    setattr(row, k, v)
                dbSession.commit()
            except Exception as e:
                logger.error("Update Error " + str(e))
        else:
            logger.debug("SariRumors 不存在 新增数据")
            try:
                new_row = SariRumors(**kwargs)
                dbSession.add(new_row)
                dbSession.commit()
            except Exception as e:
                logger.error("Insert Error " + str(e))

    def to_dict(self):
        return {
            "title": self.title,
            "mainSummary": self.mainSummary,
            "body": self.body,
            "sourceUrl": self.sourceUrl
        }


class RoleTypeEnum(Enum):
    """角色类型"""
    member = 0  # 普通用户
    admin_rw = 1  # 管理员，可读写（针对用户操作）
    admin_r = 2  # 管理员，只读


class CompanyUser(ModelBase):
    """公司、员工多对多"""
    __tablename__ = 'company_user'

    company_id = Column(Integer, ForeignKey("company.id"), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, primary_key=True)
    role_type = Column(Integer, default=RoleTypeEnum.member, comment="角色类型")

    company = relationship("Company", back_populates="user")
    user = relationship("User", back_populates="company")

    @classmethod
    def by_user_id(cls, kid):
        return dbSession.query(cls).filter_by(user_id=kid).all()

    @classmethod
    def count_by_company_id(cls, kid):
        return dbSession.query(cls).filter_by(company_id=kid).count()

    @classmethod
    def by_company_user_id(cls, user_id, company_id):
        return dbSession.query(cls).filter_by(user_id=user_id, company_id=company_id).first()

    @classmethod
    def add(cls, **kwargs):
        """增加一行数据"""
        new_row = CompanyUser(**kwargs)
        dbSession.add(new_row)
        dbSession.commit()
        return new_row

    def update(self, **kwargs):
        """根据实例更新数据"""
        ins = {'role_type': kwargs.get('role_type', RoleTypeEnum.member)}
        dbSession.query(CompanyUser).filter_by(
            company_id=self.company_id, user_id=self.user_id).update(ins)
        dbSession.commit()

    def delete(self):
        """删除一个实例"""
        dbSession.query(CompanyUser).filter_by(
            company_id=self.company_id, user_id=self.user_id).delete()

    def to_dict(self):
        return {
            "enterpriseId": self.company_id,
            "roleType": self.role_type
        }


class Company(ModelBase):
    __tablename__ = 'company'

    id = Column(Integer, autoincrement=True, primary_key=True)
    companyName = Column(String(128), comment="公司名称", index=True, unique=True)
    companyAddr = Column(String(128), comment="公司地址")
    logoPic = Column(String(255), nullable=True, comment="logo图片地址")
    user = relationship("CompanyUser", back_populates='company')
    createTime = Column(DateTime, default=datetime.now(), comment="创建时间")
    updateTime = Column(DateTime, nullable=True, comment="更新时间")

    @classmethod
    def by_id(cls, kid):
        return dbSession.query(cls).filter_by(id=kid).first()

    @classmethod
    def by_user_id(cls, kid):
        return dbSession.query(cls).filter(Company.user.any(CompanyUser.user_id == kid)).all()

    @classmethod
    def by_name(cls, name):
        return dbSession.query(cls).filter(Company.companyName == name).first()

    @classmethod
    def all(cls):
        return dbSession.query(cls).all()

    @classmethod
    def paginate(cls, page=1, page_size=10):
        start = page_size * (page - 1)
        end = page * page_size
        return dbSession.query(cls).slice(start, end).all()

    @classmethod
    def add(cls, **kwargs):
        """增加一行数据"""
        new_row = Company(**kwargs)
        dbSession.add(new_row)
        dbSession.commit()
        return new_row

    def update(self, **kwargs):
        """根据实例更新数据"""
        kwargs['updateTime'] = datetime.now()
        row = dbSession.query(Company).filter_by(id=self.id).first()
        for k, v in kwargs.items():
            setattr(row, k, v)
        dbSession.commit()
        return row

    def delete(self):
        """根据实例删除一行数据"""
        dbSession.query(Company).filter_by(id=self.id).delete()
        dbSession.commit()

    def to_dict(self):
        return {
            "companyName": self.companyName,
            "companyAddr": self.companyAddr,
            "logoPic": self.logoPic,
            "createTime": format_time(self.createTime),
            "updateTime": format_time(self.updateTime)
        }


class StatusEnum(Enum):
    normal = 0  # 健康
    isolated = 1  # 隔离
    suspected = 2  # 疑似
    confirmed = 3  # 确诊


class User(ModelBase):
    __tablename__ = 'user'

    id = Column(Integer, autoincrement=True, primary_key=True)
    userName = Column(String(32), comment="姓名")
    employeeId = Column(String(32), nullable=True, comment="工号")
    userPhone = Column(String(32), comment="手机")
    avatarPic = Column(String(255), nullable=True, comment="头像地址")
    openid = Column(String(255), unique=True, comment="微信登录openid")
    is_admin = Column(Boolean, default=False, comment="是否是联系人")
    company = relationship("CompanyUser", back_populates='user')
    checkedTime = Column(DateTime, nullable=True, comment="签到时间")  # 可用来统计当天签到情况
    checkedAddr = Column(String(32), comment="最新签到所在地区")
    checkedStatus = Column(Integer, default=StatusEnum.normal, comment="状态")  # 最新签到状态，用于统计
    createTime = Column(DateTime, default=datetime.now(), comment="创建时间")
    updateTime = Column(DateTime, nullable=True, comment="更新时间")

    @classmethod
    def by_id(cls, kid):
        return dbSession.query(cls).filter_by(id=kid).first()

    @classmethod
    def by_openid(cls, kid):
        return dbSession.query(cls).filter_by(openid=kid).first()

    @classmethod
    def by_name_phone(cls, name, phone):
        return dbSession.query(cls).filter_by(userName=name, userPhone=phone).first()

    @classmethod
    def by_enterprise_id(cls, kid, page=1, page_size=10):
        """根据企业id查询所有用户"""
        start = page_size * (page - 1)
        end = page * page_size
        return dbSession.query(cls).filter(User.company.any(CompanyUser.company_id == kid)).slice(start, end).all()

    @classmethod
    def by_enterprise_id_checked_today(cls, kid):
        """查询当天签到的最新数据"""
        dat = date.today()
        return dbSession.query(cls).filter(and_(
            User.company.any(CompanyUser.company_id == kid), cast(User.checkedTime, DATE) == dat)).all()

    @classmethod
    def count_status_checked_today(cls, enterprise_id, status):
        """查询当天签到的最新数据"""
        dat = date.today()
        return dbSession.query(cls).filter(and_(
            User.company.any(CompanyUser.company_id == enterprise_id),
            cast(User.checkedTime, DATE) == dat),
            User.checkedStatus == status
        ).count()

    @classmethod
    def by_enterprise_id_unchecked_today(cls, kid, page=1, page_size=10):
        """查询当天未签到的数据"""
        dat = date.today()
        start = page_size * (page - 1)
        end = page * page_size
        return dbSession.query(cls).filter(
            and_(User.company.any(CompanyUser.company_id == kid),
                 or_(cast(User.checkedTime, DATE) < dat, User.checkedTime.is_(None)))).slice(start, end).all()

    @classmethod
    def all(cls):
        return dbSession.query(cls).all()

    @classmethod
    def paginate(cls, page=1, page_size=10):
        start = page_size * (page - 1)
        end = page * page_size
        return dbSession.query(cls).slice(start, end).all()

    @classmethod
    def add(cls, **kwargs):
        """增加一行数据"""
        new_row = User(**kwargs)
        dbSession.add(new_row)
        dbSession.commit()
        return new_row

    def update(self, **kwargs):
        """根据实例更新数据"""
        kwargs['updateTime'] = datetime.now()
        row = dbSession.query(User).filter_by(id=self.id).first()
        for k, v in kwargs.items():
            setattr(row, k, v)
        dbSession.commit()
        return row

    def delete(self):
        """删除一个实例"""
        dbSession.query(User).filter_by(id=self.id).delete()
        dbSession.commit()

    @property
    def user_enterprise_id(self):
        """查询用户的企业id"""
        company_users = dbSession.query(CompanyUser).filter_by(user_id=self.id).all()
        if not company_users:
            return []
        return [c.company_id for c in company_users]

    def to_dict(self):
        check_time = self.checkedTime
        is_checked = bool(check_time.date() == date.today()) if check_time else False
        return {
            "userName": self.userName,
            "employeeId": self.employeeId,
            "userPhone": self.userPhone,
            "avatarPic": self.avatarPic,
            "openid": self.openid,
            "enterpriseId": self.user_enterprise_id,
            "is_checked": is_checked,
            "checkedTime": format_time(self.checkedTime),
            "checkedAddr": self.checkedAddr,
            "checkedStatus": self.checkedStatus,
            "createTime": format_time(self.createTime),
            "updateTime": format_time(self.updateTime)
        }


class CheckInRecordModel(ModelBase):
    __tablename__ = 'check_in_record'
    id = Column(Integer, autoincrement=True, primary_key=True)
    userId = Column(ForeignKey('user.id'), comment="用户ID")  # 关联用户
    province = Column(String(64), comment="省")
    city = Column(String(64), comment="市")
    district = Column(String(64), nullable=True, comment="区/县")
    address = Column(String(255), nullable=True, comment="地址")
    latitude = Column(String(64), comment="纬度")
    longitude = Column(String(64), comment="经度")
    status = Column(Integer, default=0, comment="状态")
    createTime = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)

    @classmethod
    def by_id(cls, kid):
        return dbSession.query(cls).filter_by(id=kid).first()

    @classmethod
    def by_user_id(cls, kid, page=1, page_size=10):
        start = page_size * (page - 1)
        end = page * page_size
        return dbSession.query(cls).filter_by(userId=kid).order_by(cls.createTime.desc()).slice(start, end).all()

    @classmethod
    def all(cls):
        return dbSession.query(cls).order_by(cls.createTime.desc()).all()

    @classmethod
    def paginate(cls, page=1, page_size=10):
        start = page_size * (page - 1)
        end = page * page_size
        return dbSession.query(cls).order_by(cls.createTime.desc()).slice(start, end).all()

    @classmethod
    def add(cls, **kwargs):
        """增加一行数据"""
        new_row = CheckInRecordModel(**kwargs)
        dbSession.add(new_row)
        dbSession.commit()
        return new_row

    def to_dict(self):
        return {
            "userId": self.userId,
            "province": self.province,
            "city": self.city,
            "district": self.district,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status,
            "createTime": format_time(self.createTime)
        }


def EventType():
    return [
        {"label": "点击", "value": "CLICK"},
        {"label": "获取地址", "value": "LOCATION"},
        {"label": "扫码", "value": "SCAN"},
        {"label": "跳转", "value": "VIEW"},
        {"label": "文本", "value": "TEXT"}
    ]


def MsgType():
    return [
        {"label": "文本", "value": "text"},
        {"label": "事件", "value": "event"}
    ]


def ApplyType():
    return [
        {"label": "文本", "value": "text"},
        {"label": "图片", "value": "image"},
        {"label": "新闻", "value": "news"},
        {"label": "链接跳转", "value": "view"}
    ]


class AuthReplyModel(ModelBase):
    __tablename__ = 'auto_reply'
    id = Column(Integer, autoincrement=True, primary_key=True)
    EventKey = Column(String(128), comment="自动回复关键字")
    EventType = Column(String(64), comment="类型")
    ApplyType = Column(String(64), comment="回复类型")
    MsgType = Column(String(64), comment="消息类型")
    EventValue = Column(TEXT, comment="触发返回值")
    createTime = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)
    updateTime = Column(DateTime, nullable=True, comment="更新时间")

    @classmethod
    def by_id(cls, kid):
        return dbSession.query(cls).filter_by(id=kid).first()

    @classmethod
    def get_one(cls, key, eType, msgType):
        return dbSession.query(cls) \
            .filter(and_(AuthReplyModel.EventKey == key,
                         AuthReplyModel.EventType == eType,
                         AuthReplyModel.MsgType == msgType)) \
            .first()

    @classmethod
    def all(cls):
        return dbSession.query(cls).order_by(-cls.createTime).all()

    @classmethod
    def paginate(cls, page=1, page_size=10):
        start = page_size * (page - 1)
        end = page * page_size
        return dbSession.query(cls).order_by(-cls.createTime).slice(start, end).all()

    @property
    def _createTime(self):
        if self.createTime:
            return self.createTime.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def _updateTime(self):
        if self.updateTime:
            return self.updateTime.strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            "id": self.id,
            "EventKey": self.EventKey,
            "EventType": self.EventType,
            "EventValue": self.EventValue,
            "ApplyType": self.ApplyType,
            "MsgType": self.MsgType,
            "createTime": self._createTime,
            "updateTime": self._updateTime
        }


class NewsModel(ModelBase):
    __tablename__ = 'news'
    id = Column(Integer, autoincrement=True, primary_key=True)
    Title = Column(String(128), comment="自动回复关键字")
    Description = Column(TEXT, comment="描述")
    Content = Column(TEXT, comment="内容")
    Url = Column(String(128), comment="连接地址")
    PicUrl = Column(String(128), comment="图片地址")
    createTime = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)
    updateTime = Column(DateTime, nullable=True, comment="更新时间")

    @classmethod
    def by_id(cls, kid):
        return dbSession.query(cls).filter_by(id=kid).first()

    @classmethod
    def all(cls):
        return dbSession.query(cls).order_by(-cls.createTime).all()

    @classmethod
    def paginate(cls, page=1, page_size=10):
        start = page_size * (page - 1)
        end = page * page_size
        return dbSession.query(cls).order_by(-cls.createTime).slice(start, end).all()

    @property
    def _createTime(self):
        if self.createTime:
            return self.createTime.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def _updateTime(self):
        if self.updateTime:
            return self.updateTime.strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            "id": self.id,
            "Title": self.Title,
            "Description": self.Description,
            "Content": self.Content,
            "Url": self.Url,
            "PicUrl": self.PicUrl,
            "createTime": self._createTime,
            "updateTime": self._updateTime
        }


class EpidemicPublishModel(ModelBase):
    __tablename__ = 'epidemic_publish'
    id = Column(Integer, autoincrement=True, primary_key=True)
    cityName = Column(String(128), comment="城市名称")
    regionName = Column(String(128), comment="地区名称")
    isolatedCount = Column(Integer, comment="隔离人数")
    suspectedCount = Column(Integer, comment="疑似人数")
    confirmedCount = Column(Integer, comment="确诊人数")
    curedCount = Column(Integer, comment="治愈人数")
    comment = Column(TEXT, comment="提交备注")
    createTime = Column(DateTime, default=datetime.now, comment="提交时间")
    updateTime = Column(DateTime, comment="更新时间")

    @classmethod
    def all(cls):
        return dbSession.query(cls).order_by(-cls.updateTime).all()

    @classmethod
    def add(cls, **kwargs):
        """增加一行数据"""
        new_row = EpidemicPublishModel(**kwargs)
        dbSession.add(new_row)
        dbSession.commit()
        return new_row

    @classmethod
    def update(cls, kid, data):
        """根据id更新数据，data为字典格式"""
        data['updateTime'] = datetime.now()
        dbSession.query(cls).filter_by(id=kid).update(data)
        dbSession.commit()

    @classmethod
    def update_by_city(cls, **data):
        cityName = data.get('cityName')
        regionName = data.get('regionName')
        data['updateTime'] = datetime.now()
        row = dbSession.query(cls).filter(and_(EpidemicPublishModel.regionName.like("%{}%".format(regionName)),
                                               EpidemicPublishModel.cityName.like("%{}%".format(cityName)))).first()
        if row:
            for k, v in data.items():
                setattr(row, k, v)
            dbSession.commit()
        else:
            cls.add(**data)

    @classmethod
    def delete(cls, kid):
        """根据id删除一行数据"""
        dbSession.query(cls).filter_by(id=kid).delete()
        dbSession.commit()

    @classmethod
    def by_city(cls, CityName):
        return dbSession.query(cls).order_by(-cls.updateTime) \
            .filter(cls.cityName.like('%{}%'.format(CityName))).all()

    def to_dict(self):
        return {
            "id": self.id,
            "cityName": self.cityName,
            "regionName": self.regionName,
            "isolatedCount": self.isolatedCount,
            "suspectedCount": self.suspectedCount,
            "confirmedCount": self.confirmedCount,
            "curedCount": self.curedCount,
            "comment": self.comment,
            "createTime": format_time(self.createTime),
            "updateTime": format_time(self.updateTime)
        }
