import { Step, Table, BeforeSuite, AfterSuite, TableRow } from "gauge-ts";
import { strictEqual } from "assert";
import {
  $,
  above,
  accept,
  below,
  button,
  checkBox,
  click,
  closeBrowser,
  confirm,
  evaluate,
  goto,
  image,
  into,
  link,
  openBrowser,
  press,
  screenshot,
  text,
  textBox,
  toLeftOf,
  within,
  write,
} from "taiko";
import assert = require("assert");

const frontend_url = process.env.SA_FRONTEND_URL || "http://localhost:5173";
export default class StepImplementation {
  @BeforeSuite()
  public async beforeSuite() {
    await openBrowser({ headless: true });
  }

  @AfterSuite()
  public async afterSuite() {
    await closeBrowser();
  }

  @Step("アプリケーションにアクセスする")
  public async openTodo() {
    await goto(frontend_url);
  }

  @Step("初期ページが表示される")
  public async checkFirstPage() {
    await text("React Router Contacts").exists(0, 3000);
  }

  @Step("新規に連絡先を追加する")
  public async createContact() {
    await click(button("New", within($("#sidebar"))));
  }

  @Step("<contactName> という連絡先がサイドバーに表示される")
  public async checkContactNameLinkInSideBar(contactName: string) {
    assert.ok(await link(contactName, within($("#sidebar"))).exists(0, 3000));
  }

  @Step("サイドバーから <contactName> という連絡先を選択する")
  public async selectContact(contactName: string) {
    await click(link(contactName, within($("#sidebar"))));
  }

  @Step("<contactName> という連絡先の詳細画面が表示される")
  public async checkDisplayContactDetail(contactName: string) {
    assert.ok(
      await text(new RegExp(contactName), within($("#detail"))).exists(0, 3000)
    );
    assert.ok(await button("Edit", within($("#detail"))).exists(0, 3000));
    assert.ok(await button("Delete", within($("#detail"))).exists(0, 3000));
  }

  @Step("詳細画面で編集ボタンを押下する")
  public async clickEditInDetailScreen() {
    await click(button("Edit", within($("#detail"))));
  }

  @Step("すべて空欄の編集画面が表示される")
  public async checkDisplayEditScreen() {
    await textBox({ placeholder: "First", value: "" }).exists(0, 3000);
    await textBox({ placeholder: "Last", value: "" }).exists(0, 3000);
    await textBox("Twitter").exists(0, 3000);
    await textBox("Avatar URL").exists(0, 3000);
    await textBox("Notes").exists(0, 3000);
  }

  @Step(
    "First <firstName>、Last <lastName>、Twitter <twitter>、アバターURL <avatarUrl>、Notes <notes> として登録する"
  )
  public async updateContact(
    firstName: string,
    lastName: string,
    twitter: string,
    avatarUrl: string,
    notes: string
  ) {
    await write(firstName, into(textBox({ placeholder: "First" })));
    await write(lastName, into(textBox({ placeholder: "Last" })));
    await write(twitter, into(textBox("Twitter")));
    await write(avatarUrl, into(textBox("Avatar URL")));
    await write(notes, into(textBox("Notes")));
    await click(button("Save", within($("#detail"))));
  }

  @Step(
    "詳細画面には Twitter <twitter>、アバターURL <avatarUrl>、Notes <notes> が表示されている"
  )
  public async checkDisplayContactDetailWithName(
    twitter: string,
    avatarUrl: string,
    notes: string
  ) {
    assert.ok(await text(twitter, within($("#detail"))).exists(0, 3000));
    assert.ok(
      await image({ src: avatarUrl }, within($("#detail"))).exists(0, 3000)
    );
    assert.ok(await text(notes, within($("#detail"))).exists(0, 3000));
  }

  @Step("以下の連絡先を追加する <table>")
  public async addContacts(table: Table) {
    for (var row of table.getTableRows()) {
      await click(button("New", within($("#sidebar"))));
      await link("No Name", within($("#sidebar"))).exists(0, 3000);
      await click(link("No Name", within($("#sidebar"))));
      await text("No Name", within($("#detail"))).exists(0, 3000);
      await click(button("Edit", within($("#detail"))));
      await textBox({ placeholder: "First", value: "" }).exists(0, 3000);
      await write(
        row.getCell("First"),
        into(textBox({ placeholder: "First" }))
      );
      await write(row.getCell("Last"), into(textBox({ placeholder: "Last" })));
      await write(row.getCell("Twitter"), into(textBox("Twitter")));
      await click(button("Save"));
      await link(
        `${row.getCell("First")} ${row.getCell("Last")}`,
        within($("#sidebar"))
      ).exists(0, 3000);
    }
  }

  @Step("以下の連絡先がサイドバーに表示されること <table>")
  public async checkContactsInSideBar(table: Table) {
    let before: TableRow;
    for (var row of table.getTableRows()) {
      const places = [within($("#sidebar"))];
      if (before) {
        places.push(below(text(before["Name"], within($("#sidebar")))));
      }
      await link(row.getCell("Name"), ...places).exists(0, 3000);
    }
  }

  @Step("<contactName> を検索する")
  public async searchForContactName(contactName: string) {
    await write(contactName, into(textBox(within($("#sidebar")))));
  }

  @Step("<contactName> を削除する")
  public async deleteContact(contactName: string) {
    await click(link(contactName, within($("#sidebar"))));
    await text(contactName, within($("#detail"))).exists(0, 3000);
    confirm(
      "Please confirm you want to delete this record.",
      async () => await accept()
    );
    await click(button("Delete"));
  }

  @Step("すべての連絡先を削除する")
  public async clearAllContacts() {
    // @ts-ignore
    await evaluate(() => localStorage.clear());
  }
}
