import datetime
import functools
from decimal import Decimal
from typing import List, Dict

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_migrate


# Create your models here.


class Difference(models.Model):
    """结余差异"""
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    primary = models.ForeignKey('Difference', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.code}: {self.name}'


class Subject(models.Model):
    """会计科目"""
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    primary = models.ForeignKey('Subject', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.code}: {self.name}'


class SDRelationship(models.Model):
    """科目与差异联系"""
    subject_sec = models.ForeignKey(Subject, on_delete=models.CASCADE)
    difference_sec = models.ForeignKey(Difference, on_delete=models.CASCADE)

    def __str__(self):
        return f'会计科目{self.subject_sec.code}与差异类别{self.difference_sec.code}有关'


class Document(models.Model):
    """会计凭证"""
    description = models.TextField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f'{self.date.strftime("%y-%m-%d")}: {self.description}'


class DocumentEntry(models.Model):
    """会计分录"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    debit = models.BooleanField(default=True)
    subject_sec = models.ForeignKey(Subject, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f'{"借" if self.debit else "贷"} {self.subject_sec.name} {self.amount:.2f}万元: {self.document.description}'


class DocumentDifference(models.Model):
    """会计凭证差异"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    difference_sec = models.ForeignKey(Difference, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f'{self.difference_sec.name} {self.amount:.2f}万元: {self.document.description}'


def alg_difference() -> None:
    DocumentDifference.objects.all().delete()

    S4 = Subject.objects.all().get(code='4')
    S5 = Subject.objects.all().get(code='5')
    S6 = Subject.objects.all().get(code='6')
    S7 = Subject.objects.all().get(code='7')
    D1 = Difference.objects.all().get(code='1')
    D2 = Difference.objects.all().get(code='2')
    D3 = Difference.objects.all().get(code='3')
    D4 = Difference.objects.all().get(code='4')
    D1U = Difference.objects.all().get(code='10')
    D2U = Difference.objects.all().get(code='20')
    D3U = Difference.objects.all().get(code='30')
    D4U = Difference.objects.all().get(code='40')

    for document in Document.objects.all():
        acc, bud = Decimal(0), Decimal(0)
        qs = []
        for de in DocumentEntry.objects.filter(document=document):
            if de.subject_sec.primary == S4:
                acc += de.amount
            elif de.subject_sec.primary == S5:
                bud -= de.amount
            elif de.subject_sec.primary == S6:
                acc -= de.amount
            elif de.subject_sec.primary == S7:
                bud += de.amount
            qs.append(Q(subject_sec=de.subject_sec))

        # noinspection PyTypeChecker
        q = functools.reduce(Q.__or__, qs)
        d = SDRelationship.objects.all().filter(q)

        # acc
        if acc > 0:
            # 有4缺6
            da = d.filter(difference_sec__primary=D1)
            if len(da) == 1:
                sd = da.get().difference_sec
            else:
                # unknown
                sd = D1U
            DocumentDifference.objects.create(document=document, difference_sec=sd, amount=acc)
        elif acc < 0:
            # 有6缺4
            da = d.filter(difference_sec__primary=D3)
            if len(da) == 1:
                sd = da.get().difference_sec
            else:
                # unknown
                sd = D3U
            DocumentDifference.objects.create(document=document, difference_sec=sd, amount=-acc)

        # bud
        if bud > 0:
            # 有7缺5
            da = d.filter(difference_sec__primary=D2)
            if len(da) == 1:
                sd = da.get().difference_sec
            else:
                # unknown
                sd = D2U
            DocumentDifference.objects.create(document=document, difference_sec=sd, amount=bud)

        elif bud < 0:
            # 有5缺7
            da = d.filter(difference_sec__primary=D4)
            if len(da) == 1:
                sd = da.get().difference_sec
            else:
                # unknown
                sd = D4U
            DocumentDifference.objects.create(document=document, difference_sec=sd, amount=-bud)


def initialize(*args, **kwargs):
    difference_defaults = [
        ['1', '加1.当期确认为收入但没有确认为预算收入', [
            ['10', '（0）未确定为何种情况'],
            ['11', '（1）应收款项、预收账款确认的收入'],
            ['12', '（2）接受非货币性资产捐赠确认的收入'],
        ], ],
        ['2', '加2.当期确认为预算支出但没有确认为费用', [
            ['20', '（0）未确定为何种情况'],
            ['21', '（1）支付应付款项、预付款项的支出'],
            ['22', '（2）在取得存货、政府储备物资等计入物资成本的支出'],
            ['23', '（3）为购建固定资产等的资本性支出'],
            ['24', '（4）偿还借款本息的支出'],
            ['25', '（5）取得投资的支出'],
        ], ],
        ['3', '减1.当期确认为预算收入但没有确认为收入', [
            ['30', '（0）未确定为何种情况'],
            ['31', '（1）收到应收款项、预收账款确认的预算收入'],
            ['32', '（2）取得借款确认的预算收入'],
        ], ],
        ['4', '减2.当期确认为费用但没有确认为预算支出', [
            ['40', '（0）未确定为何种情况'],
            ['41', '（1）发出存货、政府储备物资等确认的费用'],
            ['42', '（2）计提的折旧费用和摊销费用'],
            ['43', '（3）确认的资产处置费用（处置资产价值）'],
            ['44', '（4）应付款项、预付账款确认的费用'],
            ['45', '（5）计提坏账准备确认的费用'],
        ], ],
    ]
    for c, n, sub in difference_defaults:
        p = Difference.objects.get_or_create(code=c, name=n)[0]
        for _c, _n in sub:
            Difference.objects.get_or_create(code=_c, name=_n, primary=p)
    subject_defaults = [
        ['1', '财务会计科目：（一）资产类', [
            ['1001', '1001 库存现金'],
            ['1002', '1002 银行存款'],
            ['1011', '1011 零余额账户用款额度'],
            ['1021', '1021 其他货币资金'],
            ['1101', '1101 短期投资'],
            ['1201', '1201 财政应返还额度'],
            ['1211', '1211 应收票据'],
            ['1212', '1212 应收账款'],
            ['1214', '1214 预付账款'],
            ['1215', '1215 应收股利'],
            ['1216', '1216 应收利息'],
            ['1218', '1218 其他应收款'],
            ['1219', '1219 坏账准备'],
            ['1301', '1301 在途物品'],
            ['1302', '1302 库存物品'],
            ['1303', '1303 加工物品'],
            ['1401', '1401 待摊费用'],
            ['1501', '1501 长期股权投资'],
            ['1502', '1502 长期债券投资'],
            ['1601', '1601 固定资产'],
            ['1602', '1602 固定资产累计折旧'],
            ['1611', '1611 工程物资'],
            ['1613', '1613 在建工程'],
            ['1701', '1701 无形资产'],
            ['1702', '1702 无形资产累计摊销'],
            ['1703', '1703 研发支出'],
            ['1801', '1801 公共基础设施'],
            ['1802', '1802 公共基础设施累计折旧（摊销）'],
            ['1811', '1811 政府储备物资'],
            ['1821', '1821 文物文化资产'],
            ['1831', '1831 保障性住房'],
            ['1832', '1832 保障性住房累计折旧'],
            ['1891', '1891 受托代理资产'],
            ['1901', '1901 长期待摊费用'],
            ['1902', '1902 待处理财产损溢'],
        ], ],
        ['2', '财务会计科目：（二）负债类', [
            ['2001', '2001 短期借款'],
            ['2101', '2101 应交增值税'],
            ['2102', '2102 其他应交税费'],
            ['2103', '2103 应缴财政款'],
            ['2201', '2201 应付职工薪酬'],
            ['2301', '2301 应付票据'],
            ['2302', '2302 应付账款'],
            ['2303', '2303 应付政府补贴款'],
            ['2304', '2304 应付利息'],
            ['2305', '2305 预收账款'],
            ['2307', '2307 其他应付款'],
            ['2401', '2401 预提费用'],
            ['2501', '2501 长期借款'],
            ['2502', '2502 长期应付款'],
            ['2601', '2601 预计负债'],
            ['2901', '2901 受托代理负债'],
        ], ],
        ['3', '财务会计科目：（三）净资产类', [
            ['3001', '3001 累计盈余'],
            ['3101', '3101 专用基金'],
            ['3201', '3201 权益法调整'],
            ['3301', '3301 本期盈余'],
            ['3302', '3302 本年盈余分配'],
            ['3401', '3401 无偿调拨净资产'],
            ['3501', '3501 以前年度盈余调整'],
        ], ],
        ['4', '财务会计科目：（四）收入类', [
            ['4001', '4001 财政拨款收入'],
            ['4101', '4101 事业收入'],
            ['4201', '4201 上级补助收入'],
            ['4301', '4301 附属单位上缴收入'],
            ['4401', '4401 经营收入'],
            ['4601', '4601 非同级财政拨款收入'],
            ['4602', '4602 投资收益'],
            ['4603', '4603 捐赠收入'],
            ['4604', '4604 利息收入'],
            ['4605', '4605 租金收入'],
            ['4609', '4609 其他收入'],
        ], ],
        ['5', '财务会计科目：（五）费用类', [
            ['5001', '5001 业务活动费用'],
            ['5101', '5101 单位管理费用'],
            ['5201', '5201 经营费用'],
            ['5301', '5301 资产处置费用'],
            ['5401', '5401 上缴上级费用'],
            ['5501', '5501 对附属单位补助费用'],
            ['5801', '5801 所得税费用'],
            ['5901', '5901 其他费用'],
        ], ],
        ['6', '预算会计科目：（一）预算收入类', [
            ['6001', '6001 财政拨款预算收入'],
            ['6101', '6101 事业预算收入'],
            ['6201', '6201 上级补助预算收入'],
            ['6301', '6301 附属单位上缴预算收入'],
            ['6401', '6401 经营预算收入'],
            ['6501', '6501 债务预算收入'],
            ['6601', '6601 非同级财政拨款预算收入'],
            ['6602', '6602 投资预算收益'],
            ['6609', '6609 其他预算收入'],
        ], ],
        ['7', '预算会计科目：（二）预算支出类', [
            ['7101', '7101 行政支出'],
            ['7201', '7201 事业支出'],
            ['7301', '7301 经营支出'],
            ['7401', '7401 上缴上级支出'],
            ['7501', '7501 对附属单位补助支出'],
            ['7601', '7601 投资支出'],
            ['7701', '7701 债务还本支出'],
            ['7901', '7901 其他支出'],
        ], ],
        ['8', '预算会计科目：（三）预算结余类', [
            ['8001', '8001 资金结存'],
            ['8101', '8101 财政拨款结转'],
            ['8102', '8102 财政拨款结余'],
            ['8201', '8201 非财政拨款结转'],
            ['8202', '8202 非财政拨款结余'],
            ['8301', '8301 专用结余'],
            ['8401', '8401 经营结余'],
            ['8501', '8501 其他结余'],
            ['8701', '8701 非财政拨款结余分配'],
        ], ],
    ]
    for c, n, sub in subject_defaults:
        p = Subject.objects.get_or_create(code=c, name=n)[0]
        for _c, _n in sub:
            Subject.objects.get_or_create(code=_c, name=_n, primary=p)
    sd_relationship_defaults = [
        ['1212', '11'],
        ['2305', '11'],
        ['4603', '12'],
        ['1212', '21'],
        ['2305', '21'],
        ['2201', '21'],
        ['2101', '21'],
        ['2102', '21'],
        ['1301', '22'],
        ['1302', '22'],
        ['1303', '22'],
        ['1601', '23'],
        ['1701', '23'],
        ['1613', '23'],
        ['2304', '24'],
        ['1101', '25'],
        ['1501', '25'],
        ['1502', '25'],
        ['1212', '31'],
        ['2305', '31'],
        ['1215', '31'],
        ['1501', '31'],
        ['2001', '32'],
        ['2501', '32'],
        ['1301', '41'],
        ['1302', '41'],
        ['1303', '41'],
        ['1602', '42'],
        ['1702', '42'],
        ['5301', '43'],
        ['1212', '44'],
        ['2305', '44'],
        ['2201', '44'],
        ['2101', '44'],
        ['2102', '44'],
        ['1219', '45'],
    ]
    for s, d in sd_relationship_defaults:
        subject = Subject.objects.all().get(code=s)
        difference = Difference.objects.all().get(code=d)
        SDRelationship.objects.get_or_create(subject_sec=subject, difference_sec=difference)
    document_defaults = [
        ['收到“财政授权支付额度到账通知书”，金额为100万元。', datetime.date(2024, 1, 1), [
            [True, '1011', 100],
            [False, '4001', 100],
            [True, '8001', 100],
            [False, '6001', 100],
        ], ],
        ['借入短期借款10万元。', datetime.date(2024, 1, 4), [
            [True, '1002', 10],
            [False, '2001', 10],
            [True, '8001', 10],
            [False, '6501', 10],
        ], ],
        ['计算短期借款利息0.35万元。', datetime.date(2024, 1, 5), [
            [True, '5901', 0.35],
            [False, '2304', 0.35],
        ], ],
        ['年末，支付利息 0.35 万元，归还短期借款 1 万元。', datetime.date(2024, 12, 23), [
            [True, '2001', 10],
            [True, '2304', 0.35],
            [False, '1002', 10.35],
            [True, '7701', 10],
            [True, '7901', 0.35],
            [False, '8001', 10.35],
        ], ],
        ['外购经营用的办公物品5万元，验收入库，增值税0.8万元。', datetime.date(2024, 2, 1), [
            [True, '1302', 5],
            [True, '2101', 0.8],
            [False, '1011', 5.8],
            [True, '7301', 5.8],
            [False, '8001', 5.8],
        ], ],
        ['销售存货价款50万元，增值税8万元。', datetime.date(2024, 3, 1), [
            [True, '1212', 58],
            [False, '4401', 50],
            [False, '2101', 8],
        ], ],
        ['结转销售成本35万元。', datetime.date(2024, 3, 4), [
            [True, '5201', 35],
            [False, '1302', 35],
        ], ],
        ['收到应收账款58万元。', datetime.date(2024, 3, 6), [
            [True, '1002', 58],
            [False, '1212', 58],
            [True, '8001', 58],
            [False, '6401', 58],
        ], ],
        ['接受捐赠一项固定资产，成本为10万元，发生相关税费0.2万元。', datetime.date(2024, 4, 1), [
            [True, '1601', 10.2],
            [False, '1002', 0.2],
            [False, '4603', 10],
            [True, '7901', 0.2],
            [False, '8001', 0.2],
        ], ],
        ['用财政授权支付的资金购买事业单位管理用固定资产20万元。', datetime.date(2024, 5, 2), [
            [True, '1601', 20],
            [False, '1011', 20],
            [True, '7201', 20],
            [False, '8001', 20],
        ], ],
        ['单位计提开展业务活动的固定资产折旧2万元，管理活动的固定资产折旧1.5万元。', datetime.date(2024, 5, 6), [
            [True, '5001', 2],
            [True, '5101', 1.5],
            [False, '1602', 3.5],
        ], ],
        ['处置一项固定资产，账面余额为 10 万元，累计折旧为8万元，收到价款3万元，发生处置费用0.2万元。',
         datetime.date(2024, 5, 8), [
             [True, '5301', 2],
             [True, '1602', 8],
             [False, '1601', 10],
             [True, '1002', 3],
             [False, '2103', 2.8],
             [False, '1002', 0.2],
         ], ],
        ['单位购买了一项长期股权投资10万元，以银行存款支付。', datetime.date(2024, 6, 3), [
            [True, '1501', 10],
            [False, '1002', 10],
            [True, '7601', 10],
            [False, '8001', 10],
        ], ],
        ['长期股权投资采用成本法后续计量，被投资单位宣告发放现金股利1万元。', datetime.date(2024, 9, 2), [
            [True, '1215', 1],
            [False, '4602', 1],
        ], ],
        ['收到现金股利1万元。', datetime.date(2024, 9, 5), [
            [True, '1002', 1],
            [False, '1215', 1],
            [True, '8001', 1],
            [False, '6602', 1],
        ], ],
        ['计提业务人员职工薪酬30万元，管理人员职工薪酬40万元。', datetime.date(2024, 12, 2), [
            [True, '5001', 30],
            [True, '5101', 40],
            [False, '2201', 70],
        ], ],
        ['支付计提业务人员职工薪酬30万元，管理人员职工薪酬40万元。', datetime.date(2024, 12, 4), [
            [True, '2201', 70],
            [False, '1011', 70],
            [True, '7201', 70],
            [False, '8001', 70],
        ], ],
        ['假定经计算得到的应纳企业所得税为 20 万元。', datetime.date(2024, 12, 16), [
            [True, '5801', 20],
            [False, '2102', 20],
        ], ],
        ['年末注销零余额账户用款额度4.2万元。', datetime.date(2024, 12, 30), [
            [True, '1201', 4.2],
            [False, '1011', 4.2],
            [True, '8001', 4.2],
            [False, '8001', 4.2],
        ], ],
    ]
    for desc, date, entries in document_defaults:
        document = Document.objects.get_or_create(description=desc, date=date)[0]
        for debit, code, amount in entries:
            DocumentEntry.objects.get_or_create(document=document, debit=debit, subject_sec=Subject.objects.get(code=code), amount=amount)

    alg_difference()


post_migrate.connect(initialize)
