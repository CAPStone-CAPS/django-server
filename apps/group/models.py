from django.db import models
from django.contrib.auth.models import User

"""
- 그룹 정보 테이블: 
    | id (PK, INT) | name (TEXT) | description (TEXT) |
- 그룹-유저 매칭 중간 테이블 : 
| id (PK) | usergroup_id (FK → user_groups.id) | user_id (FK → auth_user.id) |
"""

class GroupInfo(models.Model):
    group_name = models.TextField()
    description = models.TextField()    # 그룹의 각오
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.group_name

    class Meta:
        db_table = 'user_groups'  # 주석에 나온 테이블 이름을 반영


class UserGroupMembership(models.Model):
    group = models.ForeignKey(GroupInfo, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} in {self.group.group_name}'

    class Meta:
        db_table = 'user_group_memberships'  # 원하는 테이블명
        unique_together = ('group', 'user')  # 중복 가입 방지